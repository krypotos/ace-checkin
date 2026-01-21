"""FastAPI application main entry point"""
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.models import EntryLog, Member, PaymentLog
from app.schemas import (
    EntryCheckIn,
    EntryResponse,
    MemberCreate,
    MemberResponse,
    PaymentCheckIn,
    PaymentResponse,
)

# Create FastAPI app
app = FastAPI(
    title="Ace Check-in API",
    description="Tennis club member check-in and payment tracking system for mobile app",
    version="2.0.0",
)

# Add CORS middleware - configured for mobile app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.environment}


# ==================== Member Management ====================


@app.post("/api/members", response_model=MemberResponse, tags=["Members"])
async def create_member(member: MemberCreate, session: Session = Depends(get_session)):
    """Create a new member"""
    db_member = Member(**member.model_dump())
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@app.get("/api/members/{member_id}", response_model=MemberResponse, tags=["Members"])
async def get_member(member_id: int, session: Session = Depends(get_session)):
    """
    Get member details by ID

    Use this to verify a scanned barcode before logging entry/payment.
    The mobile app should call this first to show member name for confirmation.
    """
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found"
        )
    return member


@app.get("/api/members", response_model=list[MemberResponse], tags=["Members"])
async def list_members(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    """List all members with pagination"""
    members = session.query(Member).offset(skip).limit(limit).all()
    return members


# ==================== Entry Management ====================


@app.post("/api/entry", response_model=EntryResponse, tags=["Entry"])
async def log_entry(entry: EntryCheckIn, session: Session = Depends(get_session)):
    """
    Log a member entry to the court

    Mobile app workflow:
    1. Scan barcode → get member_id
    2. (Optional) Call GET /api/members/{member_id} to show member name
    3. User confirms → POST /api/entry with member_id
    4. Show success with returned member_name and timestamp
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == entry.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {entry.member_id} not found",
        )

    # Create entry log
    entry_log = EntryLog(member_id=entry.member_id, notes=entry.notes)
    session.add(entry_log)
    session.commit()
    session.refresh(entry_log)

    # Return response with member details for confirmation screen
    return EntryResponse(
        id=entry_log.id,
        member_id=entry_log.member_id,
        member_name=member.name,
        timestamp=entry_log.timestamp,
        notes=entry_log.notes,
        message=f"Entry logged for {member.name}",
    )


@app.get("/api/entries/{member_id}", tags=["Entry"])
async def get_member_entries(
    member_id: int, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """Get entry history for a member"""
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found"
        )

    entries = (
        session.query(EntryLog)
        .filter(EntryLog.member_id == member_id)
        .order_by(EntryLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "member_id": member_id,
        "member_name": member.name,
        "total_entries": len(entries),
        "entries": entries,
    }


# ==================== Payment Management ====================


@app.post("/api/payment", response_model=PaymentResponse, tags=["Payment"])
async def log_payment(payment: PaymentCheckIn, session: Session = Depends(get_session)):
    """
    Log a member payment

    Mobile app workflow:
    1. Scan barcode → get member_id
    2. (Optional) Call GET /api/members/{member_id} to show member name
    3. User enters amount
    4. User confirms → POST /api/payment with member_id and amount
    5. Show success with returned details

    Note: Amount is in dollars (e.g., 25.50), stored as cents internally.
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == payment.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {payment.member_id} not found",
        )

    # Convert amount to cents (integer) for storage
    amount_cents = int(payment.amount * 100)

    # Create payment log
    payment_log = PaymentLog(member_id=payment.member_id, amount=amount_cents, notes=payment.notes)
    session.add(payment_log)
    session.commit()
    session.refresh(payment_log)

    # Return response with member details for confirmation screen
    return PaymentResponse(
        id=payment_log.id,
        member_id=payment_log.member_id,
        member_name=member.name,
        amount=payment.amount,  # Return original dollar amount
        timestamp=payment_log.timestamp,
        notes=payment_log.notes,
        message=f"Payment of ${payment.amount:.2f} logged for {member.name}",
    )


@app.get("/api/payments/{member_id}", tags=["Payment"])
async def get_member_payments(
    member_id: int, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    """Get payment history for a member"""
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found"
        )

    payments = (
        session.query(PaymentLog)
        .filter(PaymentLog.member_id == member_id)
        .order_by(PaymentLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convert amounts from cents to dollars in response
    payments_response = [
        {
            "id": p.id,
            "member_id": p.member_id,
            "amount": p.amount / 100,  # Convert to dollars
            "timestamp": p.timestamp,
            "notes": p.notes,
        }
        for p in payments
    ]

    total_cents = sum(p.amount for p in payments)

    return {
        "member_id": member_id,
        "member_name": member.name,
        "total_payments": len(payments),
        "total_amount": total_cents / 100,
        "payments": payments_response,
    }


@app.get("/api/member/{member_id}/summary", tags=["Summary"])
async def get_member_summary(member_id: int, session: Session = Depends(get_session)):
    """
    Get complete summary for a member - entries and payments

    Useful for mobile app member detail screen.
    """
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {member_id} not found"
        )

    entries = session.query(EntryLog).filter(EntryLog.member_id == member_id).all()
    payments = session.query(PaymentLog).filter(PaymentLog.member_id == member_id).all()

    total_cents = sum(p.amount for p in payments)
    last_entry = max((e.timestamp for e in entries), default=None)
    last_payment = max((p.timestamp for p in payments), default=None)

    return {
        "member": {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "phone": member.phone,
            "created_at": member.created_at,
        },
        "stats": {
            "total_entries": len(entries),
            "total_payments": len(payments),
            "total_amount_paid": total_cents / 100,
            "last_entry": last_entry,
            "last_payment": last_payment,
        },
    }
