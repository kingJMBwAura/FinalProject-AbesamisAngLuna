from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account
from django.contrib import messages
from django.utils import timezone

# Account management methods
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.check_password(password):
                request.session['account_id'] = account.pk  # request session instead of global id
                return redirect('homepage')
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid password'})
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Account does not exist'})
    else:
        return render(request, 'payroll_app/login.html')
    
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'})
        else:
            Account.objects.create(username=username, password=password)
            return redirect('login')
    else:
        return render(request, 'payroll_app/signup.html')
    
def manage_account(request, pk):
    session_id = request.session.get('account_id')
    if session_id != int(pk):
        return redirect('login')

    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST" and request.POST.get("delete_account") == "true":
        account.delete()
        request.session.flush()  # properly log out
        return redirect("login")

    return render(request, 'payroll_app/manage_account.html', {'account': account})

def change_password(request, pk):
    session_id = request.session.get('account_id')
    if session_id != int(pk):
        return redirect('login')

    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return redirect('login')

    if request.method == "POST":
        current_password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

    # FIX PART WHERE WHEN OPENED IT SAYS CURRENT PASSWORD IS INCORRECT KAAGAD
    
        if current_password != account.password:
            return render(request, 'payroll_app/change_password.html', {'error': 'Current password is incorrect', 'account': account})

        if current_password == new_password:
            return render(request, 'payroll_app/change_password.html', {'error': 'Please change current password', 'account': account})

        if new_password != confirm_password:
            return render(request, 'payroll_app/change_password.html', {'error': 'New passwords do not match', 'account': account})

        account.set_password(new_password)
        return render(request, 'payroll_app/manage_account.html', {'success': 'Password changed successfully', 'account': account})
    else:
        return render(request, 'payroll_app/change_password.html', {'account': account})

def logout(request):
    request.session.flush()  # logout
    return redirect('login')

# misc
def homepage(request):
    account_id = request.session.get('account_id')

    if account_id:
        try:
            account = get_object_or_404(Account, pk=account_id)
            employee = Employee.objects.all()
            return render(request, 'payroll_app/homepage.html', 
                          {'employee': employee, 'account': account})
        except Account.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')
    
def new_employee(request):
    account_id = request.session.get('account_id')

    if account_id:
        if request.method == "POST":
            name = request.POST.get("name")
            id_number = request.POST.get("id_number")
            rate = request.POST.get("rate")
            allowance = request.POST.get("allowance")

            # Check if all required fields are entered
            if not all([name, id_number, rate]):
                return render(request, 'payroll_app/new_employee.html', {'error': 'Enter required fields'})

            # Validate number fields
            try:
                id_number = int(id_number)
                rate = float(rate)
                allowance = float(allowance) if allowance else 0

            except ValueError:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Invalid input'})
            
            # 6 digit id number
            if len(str(id_number)) != 6:
                    return render(request, 'payroll_app/new_employee.html', {'error': 'ID must be 6 digits'})
            
            # Name cannot contain numbers
            if any(char.isdigit() for char in name):
                return render(request, 'payroll_app/new_employee.html', {'error': 'Name cannot contain numbers'})
            
            # rate cannot be negative or 0
            if rate <= 0:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Insert valid rate'})
            
            # Allowance cannot be negative
            if allowance < 0:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Insert valid allowance'})

            # Avoiding duplicate id numbers
            if Employee.objects.filter(id_number=id_number).exists():
                return render(request, 'payroll_app/new_employee.html', {'error': f'ID {id_number} already exists'})

            # Create employee
            Employee.objects.create(
                name=name,
                id_number=id_number,
                rate=rate,
                allowance=allowance
            )
            # Redirect after successful creation
            return render(request, 'payroll_app/new_employee.html', {'success' : 'Employee added successfully'})
        return render(request, 'payroll_app/new_employee.html')
    else:
        return redirect('login')
    
def delete_employee(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        employee = get_object_or_404(Employee, id_number=pk)
        employee.delete()
        return redirect('homepage')
    
    else:
        return redirect('login')

def update_employee(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        employee = get_object_or_404(Employee, id_number=pk)

        if request.method == "POST":
            name = request.POST.get("name")
            id_number = request.POST.get("id_number")
            rate = request.POST.get("rate")
            allowance = request.POST.get("allowance")

            # Check if all required fields are entered
            if not all([name, id_number, rate]):
                return render(request, 'payroll_app/update_employee.html', {'error': 'Enter required fields', 'employee': employee})

            # Validate number fields
            try:
                id_number = int(id_number)
                rate = float(rate)
                allowance = float(allowance) if allowance else 0

            except ValueError:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Invalid input', 'employee': employee})
            
            # 6 digit id number
            if len(str(id_number)) != 6:
                    return render(request, 'payroll_app/update_employee.html', {'error': 'ID must be 6 digits', 'employee': employee})
            
            # Name cannot contain numbers
            if any(char.isdigit() for char in name):
                return render(request, 'payroll_app/update_employee.html', {'error': 'Name cannot contain numbers', 'employee': employee})
            
            # rate cannot be negative or 0
            if rate <= 0:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Insert valid rate', 'employee': employee})
            
            # Allowance cannot be negative
            if allowance < 0:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Insert valid allowance', 'employee': employee})

            # Avoiding duplicate id numbers
            if Employee.objects.filter(id_number=id_number).exclude(pk=pk).exists():
                return render(request, 'payroll_app/update_employee.html', {'error': f'ID {id_number} already exists', 'employee': employee})

            # Update employee
            employee.name = name
            employee.id_number = id_number
            employee.rate = rate
            employee.allowance = allowance
            employee.save()

            # Redirect after successful update
            return redirect('homepage')
        
        return render(request, 'payroll_app/update_employee.html', {'employee': employee})
    else:
        return redirect('login')
    
def ot_update(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        account = get_object_or_404(Account, pk=account_id)
        employee = get_object_or_404(Employee, id_number=pk)

        if request.method == "POST":
            ot_hours = float(request.POST.get("ot_hours"))
            employee.overtime_pay += (employee.rate / 160) * 1.5 * ot_hours
            employee.save()
            return redirect('homepage')
        else:
            employee_list = Employee.objects.all()
            return render(request, 'payroll_app/homepage.html', {
                'employee': employee_list,
                'account': account
            })
    else:
        return redirect('login')

# payslips

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

def get_date_range(month, cycle, year):
    if cycle == 1:
        return f"{month} 1-15, {year}"
    return f"{month} 16-31, {year}"

def payroll_page(request):
    account_id = request.session.get('account_id')
    if account_id:
        employees = Employee.objects.all()
        payslips = Payslip.objects.order_by('-date_range')

        months = [(i + 1, MONTHS[i]) for i in range(12)]

        if request.method == 'POST':
            payroll_for = request.POST.get('payroll_for')
            selected_cycle = int(request.POST.get('cycle'))
            selected_month = int(request.POST.get('month'))
            selected_year = request.POST.get('year')

            month_name = MONTHS[selected_month - 1]
            date_range = get_date_range(month_name, selected_cycle, selected_year)

            if payroll_for == 'all':
                target_employees = employees
            else:
                employee_id = request.POST.get('employee_id')
                try:
                    employee = Employee.objects.get(id_number=employee_id)
                    target_employees = [employee]
                except Employee.DoesNotExist:
                    messages.error(request, f"No employee found with ID {employee_id}.")
                    return redirect('payroll_page')

            for emp in target_employees:
                # Check if payslip already exists for this period and cycle
                if Payslip.objects.filter(id_number=emp, month=month_name, year=selected_year, pay_cycle=selected_cycle).exists():
                    messages.warning(request, f"Payslip for {emp.name} - {month_name} Cycle {selected_cycle} already exists.")
                    continue

                rate = emp.rate or 0
                allowance = emp.allowance or 0
                overtime = emp.overtime_pay or 0
                earnings = rate + allowance + overtime


                if selected_cycle == 1:
                    pag_ibig = 100
                    tax = (rate/2 + allowance + overtime - pag_ibig) * 0.2 
                    total_pay = (rate/2 + allowance + overtime - pag_ibig) - tax
                    philhealth = 0
                    sss = 0
                    total_deduction = tax + philhealth + sss


                else:
                    pag_ibig = 0
                    philhealth = 0.04 * rate
                    sss = 0.045 * rate
                    tax = (rate + allowance + overtime - philhealth - sss) * 0.2 
                    total_pay = (rate + allowance + overtime - philhealth - sss) - tax
                    total_deduction = tax + philhealth + sss

                # Save payslip
                Payslip.objects.create(
                    id_number=emp,
                    month=month_name,
                    date_range=date_range,
                    year=selected_year,
                    pay_cycle=selected_cycle,
                    rate=rate,
                    earning_allowance=allowance,
                    deductions_tax=tax,
                    deductions_health=philhealth,
                    pag_ibig=pag_ibig,
                    sss=sss,
                    overtime=overtime,
                    total_pay=total_pay,
                    gross_pay=earnings,
                    total_deductions=total_deduction
                )

                # Reset overtime
                emp.resetOvertime()

                messages.success(request, f"Payslip for {emp.name} - {month_name} Cycle {selected_cycle} created.")

            return redirect('payroll_page')

        return render(request, 'payroll_app/payroll_page.html', {
            'employees': employees,
            'payslips': payslips,
            'months': months,
        })
    else:
        return redirect('login')

def view_payslip(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        payslip = get_object_or_404(Payslip, pk=pk)

        return render(request, 'payroll_app/view_payslip.html',
                    {'payslip': payslip,
                    'employee': payslip.id_number,
                    'cycle': payslip.pay_cycle,
                    'earnings': payslip,
                    'total_deductions': payslip.total_deductions,
                    'gross_pay': payslip.gross_pay,
                    'total_pay': payslip.total_pay,
                    })
    else:
        return redirect('login')