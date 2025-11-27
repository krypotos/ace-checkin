"""FastAPI application main entry point"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_session, engine
from app.models import SQLModel, EntryLog, PaymentLog, Member
from app.schemas import (
    EntryCheckIn, EntryLogResponse,
    PaymentCheckIn, PaymentLogResponse,
    MemberCreate, MemberResponse
)
from app.config import settings

# Create FastAPI app
# Note: Database tables are created by Alembic migrations, not here.
# This prevents startup errors when the database isn't ready yet.
app = FastAPI(
    title="Ace Check-in API",
    description="Tennis club member check-in and payment tracking system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
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
async def create_member(
    member: MemberCreate,
    session: Session = Depends(get_session)
):
    """Create a new member"""
    db_member = Member(**member.model_dump())
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@app.get("/api/members/{member_id}", response_model=MemberResponse, tags=["Members"])
async def get_member(
    member_id: int,
    session: Session = Depends(get_session)
):
    """Get member details by member ID"""
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    return member


@app.get("/api/members", response_model=list[MemberResponse], tags=["Members"])
async def list_members(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all members with pagination"""
    members = session.query(Member).offset(skip).limit(limit).all()
    return members


# ==================== Entry Management ====================

@app.get("/api/entry/checkin/{member_id}", response_model=EntryLogResponse, tags=["Entry"])
async def check_in_entry(
    member_id: int,
    notes: str = None,
    session: Session = Depends(get_session)
):
    """
    Record a member entry to the court via GET request (barcode scanner friendly)
    
    Barcode URL can link directly to this endpoint.
    Examples:
      - GET /api/entry/checkin/1
      - GET /api/entry/checkin/1?notes=Court+A
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    
    # Create entry log
    entry_log = EntryLog(
        member_id=member_id,
        notes=notes
    )
    session.add(entry_log)
    session.commit()
    session.refresh(entry_log)
    
    return entry_log


@app.post("/api/entry", response_model=EntryLogResponse, tags=["Entry"])
async def post_entry(
    entry: EntryCheckIn,
    session: Session = Depends(get_session)
):
    """
    Record a member entry via POST request (for API/application use)
    
    Useful for programmatic access.
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == entry.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {entry.member_id} not found"
        )
    
    # Create entry log
    entry_log = EntryLog(
        member_id=entry.member_id,
        notes=entry.notes
    )
    session.add(entry_log)
    session.commit()
    session.refresh(entry_log)
    
    return entry_log


@app.get("/api/entry/{member_id}", tags=["Entry"])
async def get_member_entries(
    member_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get entry history for a member"""
    # Verify member exists
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    
    entries = (
        session.query(EntryLog)
        .filter(EntryLog.member_id == member_id)
        .order_by(EntryLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return entries


# ==================== Payment Management ====================

@app.get("/api/payment/checkin/{member_id}", response_model=PaymentLogResponse, tags=["Payment"])
async def check_in_payment(
    member_id: int,
    amount: float,
    notes: str = None,
    session: Session = Depends(get_session)
):
    """
    Record a member payment via GET request (barcode scanner friendly)
    
    Barcode URL can link directly to this endpoint with amount as query parameter.
    Examples:
      - GET /api/payment/checkin/1?amount=25.50
      - GET /api/payment/checkin/1?amount=25.50&notes=Monthly+fee
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount must be greater than 0"
        )
    
    # Convert amount to cents (integer) for storage
    amount_cents = int(amount * 100)
    
    # Create payment log
    payment_log = PaymentLog(
        member_id=member_id,
        amount=amount_cents,
        notes=notes
    )
    session.add(payment_log)
    session.commit()
    session.refresh(payment_log)
    
    return payment_log


@app.post("/api/payment", response_model=PaymentLogResponse, tags=["Payment"])
async def post_payment(
    payment: PaymentCheckIn,
    session: Session = Depends(get_session)
):
    """
    Record a member payment via POST request (for API/application use)
    
    Useful for programmatic access.
    """
    # Verify member exists
    member = session.query(Member).filter(Member.id == payment.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {payment.member_id} not found"
        )
    
    # Convert amount to cents (integer) for storage
    amount_cents = int(payment.amount * 100)
    
    # Create payment log
    payment_log = PaymentLog(
        member_id=payment.member_id,
        amount=amount_cents,
        notes=payment.notes
    )
    session.add(payment_log)
    session.commit()
    session.refresh(payment_log)
    
    return payment_log


@app.get("/api/payment/{member_id}", tags=["Payment"])
async def get_member_payments(
    member_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get payment history for a member"""
    # Verify member exists
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    
    payments = (
        session.query(PaymentLog)
        .filter(PaymentLog.member_id == member_id)
        .order_by(PaymentLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return payments


@app.get("/api/payment/summary/{member_id}", tags=["Payment"])
async def get_payment_summary(
    member_id: int,
    session: Session = Depends(get_session)
):
    """Get payment summary for a member"""
    # Verify member exists
    member = session.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with ID {member_id} not found"
        )
    
    payments = session.query(PaymentLog).filter(PaymentLog.member_id == member_id).all()
    total_amount_cents = sum(p.amount for p in payments)
    total_amount = total_amount_cents / 100
    
    return {
        "member_id": member_id,
        "member_name": member.name,
        "total_payments": len(payments),
        "total_amount": total_amount,
        "last_payment": payments[0].timestamp if payments else None
    }

