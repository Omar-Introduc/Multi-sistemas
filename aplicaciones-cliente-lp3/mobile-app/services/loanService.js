import ApiService from './apiService';

export class LoanService {
  static async getLoans() {
    try {
      return await ApiService.getLoans();
    } catch (error) {
      console.warn('Could not fetch loans:', error);
      return this.getMockLoans();
    }
  }

  static async requestLoan(loanData) {
    try {
      // Validate loan data
      this.validateLoanData(loanData);
      
      // Call API
      const response = await ApiService.requestLoan(loanData);
      
      return {
        success: true,
        data: response,
        message: 'Solicitud de préstamo enviada exitosamente'
      };
    } catch (error) {
      console.error('Loan request error:', error);
      return {
        success: false,
        error: error.message || 'Error al enviar solicitud de préstamo'
      };
    }
  }

  static async getLoanDetails(loanId) {
    try {
      return await ApiService.getLoanDetails(loanId);
    } catch (error) {
      console.warn('Could not fetch loan details:', error);
      return this.getMockLoanDetails(loanId);
    }
  }

  static async calculateLoanPayment(amount, term, interestRate = 5.0) {
    // Calculate monthly payment using standard amortization formula
    const principal = parseFloat(amount);
    const months = parseInt(term);
    const monthlyRate = (interestRate / 100) / 12;
    
    if (months === 0) return principal;
    
    const payment = (principal * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -months));
    
    return {
      monthlyPayment: payment,
      totalAmount: payment * months,
      totalInterest: (payment * months) - principal,
      interestRate: interestRate,
      term: months
    };
  }

  static async getLoanTypes() {
    return [
      {
        id: 'personal',
        name: 'Préstamo Personal',
        minAmount: 1000,
        maxAmount: 50000,
        minTerm: 6,
        maxTerm: 60,
        interestRate: 12.5,
        description: 'Préstamo sin garantías para gastos personales'
      },
      {
        id: 'vehicle',
        name: 'Préstamo Vehicular',
        minAmount: 5000,
        maxAmount: 100000,
        minTerm: 12,
        maxTerm: 84,
        interestRate: 9.5,
        description: 'Préstamo para compra de vehículos'
      },
      {
        id: 'mortgage',
        name: 'Préstamo Hipotecario',
        minAmount: 50000,
        maxAmount: 1000000,
        minTerm: 60,
        maxTerm: 360,
        interestRate: 8.5,
        description: 'Préstamo para compra de vivienda'
      },
      {
        id: 'business',
        name: 'Préstamo Empresarial',
        minAmount: 10000,
        maxAmount: 500000,
        minTerm: 12,
        maxTerm: 120,
        interestRate: 11.0,
        description: 'Préstamo para desarrollo empresarial'
      }
    ];
  }

  static validateLoanData(data) {
    const {
      amount,
      term,
      purpose,
      income,
      employment,
      loanType,
      collateral
    } = data;

    // Amount validation
    if (!amount || amount <= 0) {
      throw new Error('El monto del préstamo debe ser mayor a 0');
    }

    if (amount < 1000) {
      throw new Error('El monto mínimo es $1,000');
    }

    if (amount > 1000000) {
      throw new Error('El monto máximo es $1,000,000');
    }

    // Term validation
    if (!term || term <= 0) {
      throw new Error('El plazo debe ser mayor a 0 meses');
    }

    if (term > 360) {
      throw new Error('El plazo máximo es 360 meses (30 años)');
    }

    // Purpose validation
    if (!purpose || purpose.trim().length < 10) {
      throw new Error('El propósito debe tener al menos 10 caracteres');
    }

    if (purpose.length > 500) {
      throw new Error('El propósito no puede exceder 500 caracteres');
    }

    // Income validation
    if (!income || income <= 0) {
      throw new Error('Los ingresos deben ser mayores a 0');
    }

    // Calculate debt-to-income ratio
    const monthlyPayment = this.calculateLoanPayment(amount, term).monthlyPayment;
    const monthlyIncome = income;
    const debtToIncomeRatio = monthlyPayment / monthlyIncome;

    if (debtToIncomeRatio > 0.40) {
      throw new Error('El ratio deuda/ingreso no puede exceder 40%');
    }

    // Employment validation
    if (!employment || employment.trim().length < 3) {
      throw new Error('La información laboral es requerida');
    }

    // Loan type validation
    if (loanType) {
      const validTypes = ['personal', 'vehicle', 'mortgage', 'business'];
      if (!validTypes.includes(loanType)) {
        throw new Error('Tipo de préstamo inválido');
      }
    }

    return true;
  }

  static getMockLoans() {
    return [
      {
        id: '1',
        type: 'personal',
        typeName: 'Préstamo Personal',
        amount: 15000,
        interestRate: 12.5,
        term: 24,
        monthlyPayment: 712.50,
        status: 'activo',
        startDate: '2024-01-15',
        nextPayment: '2025-11-15',
        remainingAmount: 8970.50,
        totalPaid: 6042.50,
        remainingPayments: 12
      },
      {
        id: '2',
        type: 'vehicle',
        typeName: 'Préstamo Vehicular',
        amount: 35000,
        interestRate: 9.5,
        term: 60,
        monthlyPayment: 739.17,
        status: 'activo',
        startDate: '2024-05-01',
        nextPayment: '2025-11-01',
        remainingAmount: 28450.75,
        totalPaid: 6549.25,
        remainingPayments: 39
      },
      {
        id: '3',
        type: 'personal',
        typeName: 'Préstamo Personal',
        amount: 5000,
        interestRate: 12.5,
        term: 12,
        monthlyPayment: 444.53,
        status: 'pagado',
        startDate: '2023-03-01',
        endDate: '2024-03-01',
        totalPaid: 5334.36,
        completed: true
      }
    ];
  }

  static getMockLoanDetails(loanId) {
    const loans = this.getMockLoans();
    const loan = loans.find(l => l.id === loanId);
    
    if (loan) {
      return {
        ...loan,
        payments: this.generatePaymentSchedule(loan),
        documents: [
          { type: 'DNI', status: 'aprobado', uploadedAt: '2024-01-10' },
          { type: 'Recibo de ingresos', status: 'aprobado', uploadedAt: '2024-01-10' },
          { type: 'Estados de cuenta', status: 'aprobado', uploadedAt: '2024-01-12' }
        ],
        guarantor: loan.type === 'mortgage' ? {
          name: 'Juan Pérez',
          relationship: 'Cónyuge',
          dni: '12345678'
        } : null
      };
    }
    
    return null;
  }

  static generatePaymentSchedule(loan) {
    const payments = [];
    const startDate = new Date(loan.startDate);
    const monthlyPayment = loan.monthlyPayment;
    const interestRate = loan.interestRate / 100 / 12;
    let remainingBalance = loan.amount;

    for (let i = 1; i <= loan.term; i++) {
      const paymentDate = new Date(startDate);
      paymentDate.setMonth(paymentDate.getMonth() + i);

      const interestPayment = remainingBalance * interestRate;
      const principalPayment = monthlyPayment - interestPayment;
      remainingBalance -= principalPayment;

      // Only include payments that haven't been made yet (for active loans)
      if (loan.status === 'activo' && paymentDate > new Date()) {
        payments.push({
          number: i,
          date: paymentDate.toISOString().split('T')[0],
          amount: monthlyPayment,
          principal: principalPayment,
          interest: interestPayment,
          balance: Math.max(0, remainingBalance),
          status: i === 1 ? 'pendiente' : 'pendiente'
        });
      } else if (loan.status === 'pagado') {
        payments.push({
          number: i,
          date: paymentDate.toISOString().split('T')[0],
          amount: monthlyPayment,
          principal: principalPayment,
          interest: interestPayment,
          balance: Math.max(0, remainingBalance),
          status: 'pagado'
        });
      }
    }

    return payments.slice(0, 12); // Show next 12 payments
  }

  static async checkLoanEligibility(income, existingLoans = []) {
    // Check maximum loans
    const activeLoans = existingLoans.filter(loan => loan.status === 'activo');
    if (activeLoans.length >= 3) {
      return {
        eligible: false,
        reason: 'Máximo de préstamos activos alcanzado (3)'
      };
    }

    // Calculate total debt-to-income ratio
    const totalMonthlyPayments = activeLoans.reduce((sum, loan) => sum + loan.monthlyPayment, 0);
    const debtToIncomeRatio = totalMonthlyPayments / income;

    if (debtToIncomeRatio > 0.40) {
      return {
        eligible: false,
        reason: `Ratio deuda/ingreso demasiado alto (${(debtToIncomeRatio * 100).toFixed(1)}%)`
      };
    }

    return {
      eligible: true,
      maxLoanAmount: income * 0.4 * 12, // 40% of annual income
      currentDebtToIncome: debtToIncomeRatio,
      maxAdditionalPayment: Math.max(0, income * 0.40 - totalMonthlyPayments)
    };
  }

  static formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  }

  static formatPercentage(rate) {
    return `${rate.toFixed(2)}%`;
  }

  static calculateDaysUntilNextPayment(nextPaymentDate) {
    const today = new Date();
    const nextPayment = new Date(nextPaymentDate);
    const diffTime = nextPayment.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays;
  }
}

export default LoanService;