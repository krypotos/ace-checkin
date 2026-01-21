import { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, TouchableOpacity, SafeAreaView } from 'react-native';
import BarcodeScanner from './src/components/BarcodeScanner';

type Screen = 'home' | 'scanner';
type ScanMode = 'entry' | 'payment';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');
  const [scanMode, setScanMode] = useState<ScanMode>('entry');
  const [lastScannedMember, setLastScannedMember] = useState<number | null>(null);

  const handleStartScan = (mode: ScanMode) => {
    setScanMode(mode);
    setCurrentScreen('scanner');
  };

  const handleScanComplete = (memberId: number) => {
    setLastScannedMember(memberId);
    setCurrentScreen('home');

    // For now, just show an alert with the scanned ID
    // Later we'll connect this to the API
    const action = scanMode === 'entry' ? 'Entry' : 'Payment';
    alert(`${action} scan successful!\n\nMember ID: ${memberId}\n\n(API integration coming next)`);
  };

  const handleCancelScan = () => {
    setCurrentScreen('home');
  };

  if (currentScreen === 'scanner') {
    return <BarcodeScanner onScan={handleScanComplete} onCancel={handleCancelScan} />;
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.logo}>🎾</Text>
        <Text style={styles.title}>Ace Check-in</Text>
        <Text style={styles.subtitle}>Tennis Club Management</Text>
      </View>

      {/* Main Actions */}
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

      {/* Last scan info */}
      {lastScannedMember && (
        <View style={styles.lastScanContainer}>
          <Text style={styles.lastScanLabel}>Last scanned</Text>
          <Text style={styles.lastScanValue}>Member #{lastScannedMember}</Text>
        </View>
      )}

      {/* Footer */}
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
  lastScanContainer: {
    alignItems: 'center',
    paddingVertical: 20,
    marginHorizontal: 24,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    marginBottom: 20,
  },
  lastScanLabel: {
    fontSize: 12,
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  lastScanValue: {
    fontSize: 18,
    fontWeight: '600',
    color: '#10B981',
    marginTop: 4,
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 14,
    color: '#64748B',
  },
});
