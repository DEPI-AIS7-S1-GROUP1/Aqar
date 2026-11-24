# AqarAI Calculator Reference Sheet Notes

SHEET LINK: (I will paste after upload)

Member 2 reviewed the inputs only.

---

## 1. NPV Monthly Rate Convention

The calculator reference sheet uses **Convention A (Effective Monthly Compounding)** as agreed with Member 4:

- **Monthly Discount Rate Formula**:
  $$monthly\_rate = (1 + annual\_discount\_rate)^{1/12} - 1$$
- **Discount Factor in Month $t$**:
  $$DF_t = \frac{1}{(1 + monthly\_rate)^t} = \frac{1}{(1 + annual\_discount\_rate)^{t / 12}}$$
- **Month 0 Discount Factor**:
  $$DF_0 = \frac{1}{(1 + monthly\_rate)^0} = 1.0$$
  Month 0 cashflows (down payments) are undiscounted.
- **Zero Discount Rate Identity**:
  At an annual discount rate of 0%, $monthly\_rate = 0$ and $DF_t = 1.0$ for all $t$. Thus, $NPV = total\_paid$ identically across all cases.
- **Reference Spreadsheet Implementation**:
  ```excel
  =SUMPRODUCT(cashflow!B{row}:FZ{row}, 1 / ((1 + ((1 + inputs!L{row}/100)^(1/12) - 1)) ^ cashflow!$B$1:$FZ$1))
  ```

---

## 2. Installment and Month Conventions

### Developer Plans
- **Down Payment**:
  $$down = price\_egp \times \frac{down\_payment\_pct}{100}$$
  Paid in **Month 0**.
- **Delivery Payment**:
  $$delivery = price\_egp \times \frac{delivery\_payment\_pct}{100}$$
  (Blank if not published/applicable; treated as 0 for calculation). Paid in **Month `delivery_month`**.
- **Remaining Amount**:
  $$remaining = price\_egp - down - delivery$$
- **Installment Count**:
  - Monthly: $years \times 12$
  - Quarterly: $years \times 4$
- **Installment Amount**:
  $$installment = \frac{remaining}{count}$$
  (No rounding applied).
- **Payment Schedule**:
  - Month 0: Down payment only.
  - Months 1..$n$: Regular installments due monthly ($1..years \times 12$) or quarterly (months $3, 6, 9, \dots$).
  - Delivery Month: Delivery payment due in month $t = delivery\_month$. If this coincides with an installment month, the month's total cashflow is installment + delivery payment.
- **Maintenance**:
  Maintenance fees (e.g., 8-10%) are recorded as an informative percentage when available, but are **NOT** part of the property price check and are excluded from total paid and NPV calculations.

### Bank Financing Plans
- **Loan Amount**:
  $$loan = price\_egp - down$$
- **Monthly Payment (PMT)**:
  $$PMT = PMT\left(\frac{annual\_rate\_pct / 100}{12}, years \times 12, -loan\right)$$
- **Payment Schedule**:
  - Month 0: Down payment ($price\_egp \times down\_payment\_pct / 100$).
  - Months 1..$years \times 12$: Monthly payment (PMT).
- **Total Paid**:
  $$total\_paid = down + PMT \times (years \times 12)$$

### Edge Cases
- **100% Down Payment (Cases 20, 21)**:
  - Down payment = full property price (paid in Month 0).
  - Installment amount shows `0`.
  - Cashflows in Months 1..180 are `0`.
  - Total paid = $price\_egp$, and NPV = $price\_egp$ (undiscounted at Month 0).
- **0% Down Payment (Cases 18, 19)**:
  - Down payment = `0` (a genuine numerical zero).
  - The entire price (minus delivery payment if applicable) is amortized over the installment count.

---

## 3. Test Case Groups (25 Cases Total)

1. **`dev_monthly`** (Cases 01–06): 6 developer plans with 0% interest paid monthly over 5 to 10 years.
2. **`dev_quarterly`** (Cases 07–12): 6 developer plans with 0% interest paid quarterly over 5 to 10 years.
3. **`financing`** (Cases 13–17): 5 bank/mortgage financing plans with interest rates spanning 8% to 24% and terms from 5 to 15 years.
4. **`zero_down`** (Cases 18–19): 2 plans with 0% down payment (a real 0).
5. **`full_down`** (Cases 20–21): 2 plans with 100% down payment (installment amount = 0, NPV = price).
6. **`dev_delivery`** (Cases 22–25): 4 developer plans featuring delivery payments (10% to 15%) scheduled at delivery months 24, 36, or 48.

---

## 4. Data Standards
- Unknown or non-applicable values are left blank / empty, never entered as 0.
- Numerical `0` represents a true zero (such as 0% down payment or 0% discount rate).
