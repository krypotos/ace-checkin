import { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import BarcodeScanner from './src/components/BarcodeScanner';
import { api, ApiServiceError } from './src/services';
import type { Member, EntryResponse, PaymentResponse } from './src/types';

type Screen = 'home' | 'scanner' | 'confirm' | 'success';
type ScanMode = 'entry' | 'payment';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  const [scanMode, setScanMode] = useState<ScanMode>('entry');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Member state
  const [scannedMemberId, setScannedMemberId] = useState<number | null>(null);
  const [member, setMember] = useState<Member | null>(null);

  // Payment state
  const [paymentAmount, setPaymentAmount] = useState('');

  // Success state
  const [successMessage, setSuccessMessage] = useState('');
  const [successDetails, setSuccessDetails] = useState('');

  // Check API health on mount
  useEffect(() => {
    api.healthCheck().then((healthy) => {
      if (!healthy) {
        Alert.alert(
          'Connection Issue',
          'Unable to connect to the server. Please check your network connection.',
          [{ text: 'OK' }]
        );
      }
    });
  }, []);

  const handleStartScan = (mode: ScanMode) => {
    setScanMode(mode);
    setError(null);
    setCurrentScreen('scanner');
  };

  const handleScanComplete = async (memberId: number) => {
    setScannedMemberId(memberId);
    setIsLoading(true);
    setError(null);

    try {
      const memberData = await api.getMember(memberId);
      setMember(memberData);
      setCurrentScreen('confirm');
    } catch (err) {
      if (err instanceof ApiServiceError) {
        if (err.isNotFound) {
          setError(`Member #${memberId} not found`);
        } else if (err.isNetworkError) {
          setError('Network error. Please check your connection.');
        } else {
          setError(err.message);
        }
      } else {
        setError('An unexpected error occurred');
      }
      setCurrentScreen('home');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!member) return;

    setIsLoading(true);
    setError(null);

    try {
      if (scanMode === 'entry') {
        const response: EntryResponse = await api.logEntry({
          member_id: member.id,
        });
        setSuccessMessage(response.message);
        setSuccessDetails(new Date(response.timestamp).toLocaleString());
      } else {
        const amount = parseFloat(paymentAmount);
        if (isNaN(amount) || amount <= 0) {
          setError('Please enter a valid amount');
          setIsLoading(false);
          return;
        }
        const response: PaymentResponse = await api.logPayment({
          member_id: member.id,
          amount: amount,
        });
        setSuccessMessage(response.message);
        setSuccessDetails(new Date(response.timestamp).toLocaleString());
      }
      setCurrentScreen('success');
    } catch (err) {
      if (err instanceof ApiServiceError) {
        setError(err.message);
      } else {
        setError('Failed to process request');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setMember(null);
    setScannedMemberId(null);
    setPaymentAmount('');
    setError(null);
    setCurrentScreen('home');
  };

  const handleSuccessDone = () => {
    setMember(null);
    setScannedMemberId(null);
    setPaymentAmount('');
    setSuccessMessage('');
    setSuccessDetails('');
    setCurrentScreen('home');
  };

  // Scanner Screen
  if (currentScreen === 'scanner') {
    return <BarcodeScanner onScan={handleScanComplete} onCancel={handleCancel} />;
  }

  // Loading Overlay
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#10B981" />
        <Text style={styles.loadingText}>Processing...</Text>
      </View>
    );
  }

  // Confirmation Screen
  if (currentScreen === 'confirm' && member) {
    return (
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <SafeAreaView style={styles.container}>
          <StatusBar style="light" />

          <View style={styles.confirmHeader}>
            <Text style={styles.confirmIcon}>
              {scanMode === 'entry' ? '📍' : '💳'}
            </Text>
            <Text style={styles.confirmTitle}>
              {scanMode === 'entry' ? 'Confirm Entry' : 'Confirm Payment'}
            </Text>
          </View>

          <View style={styles.memberCard}>
            <Text style={styles.memberLabel}>Member</Text>
            <Text style={styles.memberName}>{member.name}</Text>
            <Text style={styles.memberId}>ID: #{member.id}</Text>
          </View>

          {scanMode === 'payment' && (
            <View style={styles.amountContainer}>
              <Text style={styles.amountLabel}>Payment Amount</Text>
              <View style={styles.amountInputContainer}>
                <Text style={styles.currencySymbol}>$</Text>
                <TextInput
                  style={styles.amountInput}
                  value={paymentAmount}
                  onChangeText={setPaymentAmount}
                  placeholder="0.00"
                  placeholderTextColor="#64748B"
                  keyboardType="decimal-pad"
                  autoFocus
                />
              </View>
            </View>
          )}

          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <View style={styles.confirmActions}>
            <TouchableOpacity
              style={[styles.confirmButton, styles.confirmButtonPrimary]}
              onPress={handleConfirm}
            >
              <Text style={styles.confirmButtonText}>
                {scanMode === 'entry' ? 'Check In' : 'Record Payment'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.confirmButton, styles.confirmButtonSecondary]}
              onPress={handleCancel}
            >
              <Text style={styles.confirmButtonTextSecondary}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </KeyboardAvoidingView>
    );
  }

  // Success Screen
  if (currentScreen === 'success') {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />

        <View style={styles.successContainer}>
          <Text style={styles.successIcon}>✅</Text>
          <Text style={styles.successTitle}>Success!</Text>
          <Text style={styles.successMessage}>{successMessage}</Text>
          <Text style={styles.successDetails}>{successDetails}</Text>

          <TouchableOpacity
            style={styles.successButton}
            onPress={handleSuccessDone}
          >
            <Text style={styles.successButtonText}>Done</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Home Screen
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      <View style={styles.header}>
        <Text style={styles.logo}>🎾</Text>
        <Text style={styles.title}>Ace Check-in</Text>
        <Text style={styles.subtitle}>Tennis Club Management</Text>
      </View>

      {error && (
        <View style={styles.homeErrorContainer}>
          <Text style={styles.homeErrorText}>{error}</Text>
        </View>
      )}

      <View style={styles.actionsContainer}>
        <TouchableOpacity
          style={[styles.actionButton, styles.entryButton]}
          onPress={() => handleStartScan('entry')}
        >
          <Text style={styles.actionIcon}>📍</Text>
          <Text style={styles.actionTitle}>Check In</Text>
          <Text style={styles.actionDescription}>Log member court entry</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.paymentButton]}
          onPress={() => handleStartScan('payment')}
        >
          <Text style={styles.actionIcon}>💳</Text>
          <Text style={styles.actionTitle}>Payment</Text>
          <Text style={styles.actionDescription}>Record member payment</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Scan member QR code to begin</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0F172A',
  },

  // Loading
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0F172A',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#94A3B8',
    fontSize: 16,
    marginTop: 16,
  },

  // Home Screen
  header: {
    alignItems: 'center',
    paddingTop: 40,
    paddingBottom: 30,
  },
  logo: {
    fontSize: 64,
    marginBottom: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#F8FAFC',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontSize: 16,
    color: '#94A3B8',
    marginTop: 4,
  },
  actionsContainer: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 20,
    gap: 16,
  },
  actionButton: {
    borderRadius: 20,
    padding: 28,
    alignItems: 'center',
  },
  entryButton: {
    backgroundColor: '#065F46',
  },
  paymentButton: {
    backgroundColor: '#1E40AF',
  },
  actionIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#F8FAFC',
    marginBottom: 4,
  },
  actionDescription: {
    fontSize: 14,
    color: '#D1D5DB',
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 14,
    color: '#64748B',
  },
  homeErrorContainer: {
    marginHorizontal: 24,
    padding: 16,
    backgroundColor: '#7F1D1D',
    borderRadius: 12,
    marginBottom: 16,
  },
  homeErrorText: {
    color: '#FCA5A5',
    fontSize: 14,
    textAlign: 'center',
  },

  // Confirmation Screen
  confirmHeader: {
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 40,
  },
  confirmIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  confirmTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#F8FAFC',
  },
  memberCard: {
    marginHorizontal: 24,
    padding: 24,
    backgroundColor: '#1E293B',
    borderRadius: 16,
    alignItems: 'center',
  },
  memberLabel: {
    fontSize: 12,
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  memberName: {
    fontSize: 28,
    fontWeight: '700',
    color: '#F8FAFC',
    marginTop: 8,
  },
  memberId: {
    fontSize: 14,
    color: '#64748B',
    marginTop: 4,
  },
  amountContainer: {
    marginHorizontal: 24,
    marginTop: 24,
  },
  amountLabel: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 8,
    textAlign: 'center',
  },
  amountInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  currencySymbol: {
    fontSize: 32,
    fontWeight: '600',
    color: '#10B981',
    marginRight: 8,
  },
  amountInput: {
    fontSize: 32,
    fontWeight: '600',
    color: '#F8FAFC',
    minWidth: 120,
    textAlign: 'center',
  },
  errorContainer: {
    marginHorizontal: 24,
    marginTop: 16,
    padding: 12,
    backgroundColor: '#7F1D1D',
    borderRadius: 8,
  },
  errorText: {
    color: '#FCA5A5',
    fontSize: 14,
    textAlign: 'center',
  },
  confirmActions: {
    marginTop: 'auto',
    paddingHorizontal: 24,
    paddingBottom: 40,
    gap: 12,
  },
  confirmButton: {
    padding: 18,
    borderRadius: 14,
    alignItems: 'center',
  },
  confirmButtonPrimary: {
    backgroundColor: '#10B981',
  },
  confirmButtonSecondary: {
    backgroundColor: '#374151',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
  confirmButtonTextSecondary: {
    color: '#D1D5DB',
    fontSize: 18,
    fontWeight: '600',
  },

  // Success Screen
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  successIcon: {
    fontSize: 80,
    marginBottom: 24,
  },
  successTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#10B981',
    marginBottom: 16,
  },
  successMessage: {
    fontSize: 18,
    color: '#F8FAFC',
    textAlign: 'center',
    marginBottom: 8,
  },
  successDetails: {
    fontSize: 14,
    color: '#94A3B8',
  },
  successButton: {
    marginTop: 48,
    backgroundColor: '#1E293B',
    paddingHorizontal: 48,
    paddingVertical: 16,
    borderRadius: 12,
  },
  successButtonText: {
    color: '#F8FAFC',
    fontSize: 18,
    fontWeight: '600',
  },
});
