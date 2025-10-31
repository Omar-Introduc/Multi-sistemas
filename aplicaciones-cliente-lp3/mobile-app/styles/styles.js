import { StyleSheet } from 'react-native';
import { theme } from './theme';

export const styles = StyleSheet.create({
  // Layout base
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  content: {
    flex: 1,
    padding: theme.spacing.md,
  },
  scrollView: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    ...theme.shadows.small,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  headerSubtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },

  // Cards
  card: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    margin: theme.spacing.sm,
    ...theme.shadows.small,
  },
  balanceCard: {
    backgroundColor: theme.colors.primary,
    margin: theme.spacing.md,
  },
  accountCard: {
    marginVertical: theme.spacing.xs,
  },
  transactionCard: {
    marginVertical: theme.spacing.xs,
  },
  historyCard: {
    marginVertical: theme.spacing.xs,
  },
  paymentCard: {
    backgroundColor: theme.colors.surface,
  },
  qrCard: {
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
  },
  formCard: {
    margin: theme.spacing.md,
  },
  infoCard: {
    backgroundColor: theme.colors.info + '10',
    borderLeftWidth: 4,
    borderLeftColor: theme.colors.info,
  },
  calculatorCard: {
    backgroundColor: theme.colors.success + '10',
    alignItems: 'center',
  },
  summaryCard: {
    margin: theme.spacing.md,
    backgroundColor: theme.colors.secondary,
  },

  // Inputs
  inputContainer: {
    marginBottom: theme.spacing.md,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    fontSize: 16,
    backgroundColor: theme.colors.surface,
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },

  // Buttons
  button: {
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.sm,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    ...theme.shadows.small,
  },
  buttonDisabled: {
    backgroundColor: theme.colors.disabled,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  generateButton: {
    marginTop: theme.spacing.md,
  },
  submitButton: {
    margin: theme.spacing.md,
  },
  secondaryButton: {
    backgroundColor: theme.colors.secondary,
  },
  confirmButton: {
    backgroundColor: theme.colors.success,
  },
  shareButton: {
    backgroundColor: theme.colors.accent,
  },
  filterButton: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginRight: theme.spacing.sm,
  },
  filterButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  filterButtonText: {
    color: theme.colors.textSecondary,
    fontSize: 14,
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#fff',
  },
  filterContainer: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  logoutButton: {
    padding: theme.spacing.sm,
  },
  logoutText: {
    color: theme.colors.error,
    fontWeight: '500',
  },
  newTransactionButton: {
    position: 'absolute',
    bottom: theme.spacing.lg,
    right: theme.spacing.lg,
    backgroundColor: theme.colors.primary,
    borderRadius: 50,
    width: 56,
    height: 56,
    alignItems: 'center',
    justifyContent: 'center',
    ...theme.shadows.medium,
  },
  newTransactionButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },

  // Balance
  balanceTitle: {
    fontSize: 16,
    color: '#fff',
    opacity: 0.9,
  },
  balanceAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginVertical: theme.spacing.sm,
  },
  balanceDate: {
    fontSize: 14,
    color: '#fff',
    opacity: 0.8,
  },

  // Actions
  quickActions: {
    margin: theme.spacing.md,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: theme.spacing.md,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: theme.spacing.xs,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    alignItems: 'center',
  },

  // Transactions
  transactionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transactionDescription: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.text,
  },
  transactionDate: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  transactionAmount: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  amountPositive: {
    color: theme.colors.success,
  },
  amountNegative: {
    color: theme.colors.error,
  },
  transactionFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: theme.spacing.md,
    paddingTop: theme.spacing.md,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  transactionCategory: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  transactionStatus: {
    fontSize: 14,
    fontWeight: '500',
    color: theme.colors.success,
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.md,
  },
  transactionText: {
    fontSize: 16,
    color: theme.colors.text,
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  transactionAmountPositive: {
    color: theme.colors.success,
  },
  transactionAmountNegative: {
    color: theme.colors.error,
  },
  transactionDivider: {
    height: 1,
    backgroundColor: theme.colors.border,
    marginVertical: theme.spacing.sm,
  },

  // Accounts
  accountHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  accountType: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  accountNumber: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  accountBalance: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  accountStatus: {
    fontSize: 14,
    color: theme.colors.success,
    fontWeight: '500',
  },

  // History
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: theme.spacing.sm,
  },
  historyIcon: {
    fontSize: 24,
    marginRight: theme.spacing.md,
  },
  historyInfo: {
    flex: 1,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.text,
  },
  historyDate: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  historyStatus: {
    alignItems: 'flex-end',
  },
  historyStatusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  historyDetails: {
    marginTop: theme.spacing.sm,
  },
  historyDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  historyAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: theme.spacing.xs,
  },
  historyAdditional: {
    marginTop: theme.spacing.sm,
    paddingTop: theme.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  additionalInfo: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    fontStyle: 'italic',
  },

  // QR Code
  qrContainer: {
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  qrCodeContainer: {
    margin: theme.spacing.lg,
    padding: theme.spacing.md,
    backgroundColor: '#fff',
    borderRadius: theme.borderRadius.md,
    ...theme.shadows.medium,
  },
  qrTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  qrAmount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  qrDescription: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.md,
  },
  qrInstructions: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginTop: theme.spacing.md,
  },
  qrButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.lg,
    width: '100%',
  },
  qrActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: theme.spacing.lg,
    width: '100%',
  },
  qrActionButton: {
    flex: 1,
    marginHorizontal: theme.spacing.sm,
  },
  qrInfo: {
    alignItems: 'center',
    marginTop: theme.spacing.md,
  },

  // Scanner
  scannerContainer: {
    flex: 1,
    position: 'relative',
  },
  scanner: {
    flex: 1,
  },
  scannerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: 200,
    height: 200,
    borderWidth: 2,
    borderColor: '#fff',
    borderRadius: theme.borderRadius.md,
    backgroundColor: 'transparent',
  },
  scanInstructions: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginTop: theme.spacing.lg,
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
  },
  scanButtons: {
    position: 'absolute',
    bottom: theme.spacing.xl,
    left: 0,
    right: 0,
    alignItems: 'center',
  },

  // Payment
  paymentTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  paymentInfo: {
    alignItems: 'center',
    marginBottom: theme.spacing.xl,
  },
  paymentAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  paymentDescription: {
    fontSize: 16,
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  paymentMerchant: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  paymentButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },

  // Form
  formTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.lg,
    textAlign: 'center',
  },

  // Calculator
  calculatorTitle: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  calculatorAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: theme.spacing.sm,
  },
  calculatorInfo: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },

  // Info
  infoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  infoText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
    lineHeight: 20,
  },

  // Lists
  listContainer: {
    paddingHorizontal: theme.spacing.md,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: theme.spacing.md,
  },
  emptyText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  summaryContainer: {
    padding: theme.spacing.md,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: theme.spacing.sm,
  },
  summaryText: {
    fontSize: 14,
    color: '#fff',
  },
  summaryAmount: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },

  // Modal
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalCard: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.xl,
    borderRadius: theme.borderRadius.md,
    alignItems: 'center',
    margin: theme.spacing.lg,
  },
  modalText: {
    fontSize: 16,
    color: theme.colors.text,
  },

  // Additional
  noCameraText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  linkText: {
    color: theme.colors.primary,
    textAlign: 'center',
    marginTop: theme.spacing.lg,
    fontSize: 14,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.primary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.xxl,
  },
  filterText: {
    color: theme.colors.primary,
    fontWeight: '500',
  },

  // Additional styles for enhanced functionality
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  refreshButton: {
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginLeft: theme.spacing.sm,
  },

  // Transaction enhanced styles
  transactionInfo: {
    flex: 1,
  },
  transactionAmountContainer: {
    alignItems: 'flex-end',
  },
  transactionReference: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
    fontStyle: 'italic',
  },
  transactionBalance: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginTop: theme.spacing.xs,
  },
  transactionCard: {
    marginVertical: theme.spacing.xs,
  },
  categoryContainer: {
    flex: 1,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: theme.spacing.sm,
  },

  // Stats styles
  statsCard: {
    margin: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    backgroundColor: theme.colors.surface,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginBottom: theme.spacing.xs,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    textAlign: 'center',
  },
  incomeText: {
    color: theme.colors.success,
  },
  expenseText: {
    color: theme.colors.error,
  },

  // Filter modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  modalClose: {
    fontSize: 16,
    color: theme.colors.primary,
    fontWeight: '500',
  },
  modalContent: {
    flex: 1,
    padding: theme.spacing.md,
  },
  filterSection: {
    marginBottom: theme.spacing.md,
  },
  filterSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  searchInput: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    fontSize: 16,
    backgroundColor: theme.colors.surface,
  },
  dateFilters: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  dateInput: {
    flex: 1,
    marginHorizontal: theme.spacing.xs,
  },
  amountFilters: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.md,
  },
  amountInput: {
    flex: 1,
    marginHorizontal: theme.spacing.xs,
  },
  textInput: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    fontSize: 16,
    backgroundColor: theme.colors.surface,
  },
  dateTextInput: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.borderRadius.sm,
    padding: theme.spacing.md,
    fontSize: 14,
    backgroundColor: theme.colors.surface,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: theme.spacing.lg,
  },
  clearButton: {
    backgroundColor: theme.colors.error,
    flex: 1,
    marginRight: theme.spacing.sm,
  },
  applyButton: {
    backgroundColor: theme.colors.success,
    flex: 1,
    marginLeft: theme.spacing.sm,
  },

  // Enhanced QR styles
  qrContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  qrDisplayCard: {
    margin: theme.spacing.md,
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.surface,
    alignItems: 'center',
  },
  typeSelector: {
    margin: theme.spacing.md,
    marginBottom: theme.spacing.sm,
  },
  typeButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  typeButton: {
    flex: 1,
    padding: theme.spacing.md,
    marginHorizontal: theme.spacing.xs,
    borderRadius: theme.borderRadius.sm,
    backgroundColor: '#f0f0f0',
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: theme.colors.primary,
  },
  typeIcon: {
    fontSize: 24,
    marginBottom: theme.spacing.sm,
  },
  typeLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  typeLabelActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  formSection: {
    marginBottom: theme.spacing.lg,
  },
  generateButton: {
    backgroundColor: theme.colors.success,
    marginTop: theme.spacing.lg,
  },
  copyButton: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.primary,
    borderRadius: theme.borderRadius.sm,
  },
  copyButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  clearButton: {
    backgroundColor: theme.colors.error,
    flex: 1,
  },
  closeButton: {
    backgroundColor: '#666',
  },
  footer: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },

  // Component-specific enhancements
  scannerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cornerTL: {
    position: 'absolute',
    top: '25%',
    left: '15%',
    width: 50,
    height: 50,
    borderTopWidth: 4,
    borderLeftWidth: 4,
    borderColor: '#fff',
  },
  cornerTR: {
    position: 'absolute',
    top: '25%',
    right: '15%',
    width: 50,
    height: 50,
    borderTopWidth: 4,
    borderRightWidth: 4,
    borderColor: '#fff',
  },
  cornerBL: {
    position: 'absolute',
    bottom: '25%',
    left: '15%',
    width: 50,
    height: 50,
    borderBottomWidth: 4,
    borderLeftWidth: 4,
    borderColor: '#fff',
  },
  cornerBR: {
    position: 'absolute',
    bottom: '25%',
    right: '15%',
    width: 50,
    height: 50,
    borderBottomWidth: 4,
    borderRightWidth: 4,
    borderColor: '#fff',
  },
  instructionText: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    textAlign: 'center',
    color: '#fff',
    fontSize: 16,
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingVertical: theme.spacing.md,
    marginHorizontal: theme.spacing.lg,
    borderRadius: theme.borderRadius.sm,
  },
  resultContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
  },
  resultCard: {
    width: '100%',
    maxWidth: 400,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
    color: theme.colors.text,
  },
  resultContent: {
    marginBottom: theme.spacing.lg,
  },
  paymentInfo: {
    marginBottom: theme.spacing.lg,
  },
  transferInfo: {
    marginBottom: theme.spacing.lg,
  },
  infoLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginTop: theme.spacing.md,
  },
  infoValue: {
    fontSize: 16,
    color: theme.colors.text,
    marginBottom: theme.spacing.sm,
  },
  buttonContainer: {
    marginVertical: theme.spacing.md,
  },
  processButton: {
    marginVertical: theme.spacing.sm,
  },
  actionButtons: {
    marginTop: theme.spacing.lg,
  },
  actionButton: {
    backgroundColor: theme.colors.primary,
  },
  permissionCard: {
    margin: theme.spacing.lg,
    padding: theme.spacing.xl,
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
  },
  permissionText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
    color: theme.colors.text,
  },
  permissionButton: {
    marginVertical: theme.spacing.sm,
  },

  // Empty card styles
  emptyCard: {
    margin: theme.spacing.lg,
    padding: theme.spacing.xl,
    alignItems: 'center',
    backgroundColor: theme.colors.surface,
  },

  // Additional utility styles
  noCameraText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  permissionButton: {
    marginVertical: theme.spacing.sm,
  },
  closeButton: {
    backgroundColor: '#666',
  },
});
