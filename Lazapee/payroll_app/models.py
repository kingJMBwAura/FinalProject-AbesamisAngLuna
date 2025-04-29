from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=50)
    id_number = models.CharField(max_length=30, primary_key=True)
    rate = models.FloatField(null=True, blank=True)
    overtime_pay = models.FloatField(null=True, blank=True)
    allowance = models.FloatField(null=True, blank=True)

    def getName(self):
        return self.name

    def getID(self):
        return self.id_number

    def getRate(self):
        return self.rate

    def getOvertime(self):
        return self.overtime_pay

    def resetOvertime(self):
        self.overtime_pay = 0
        self.save() # reset and saves ot pay to 0

    def getAllowance(self):
        return self.allowance

    def str(self):
        return f"{self.id_number} : {self.name} (Rate: {self.rate:.2f})"

    class Meta:
        ordering = ['name'] # arranges names

class Payslip(models.Model):
    id_number = models.ForeignKey(Employee, on_delete=models.CASCADE) # when payslip deleted, delete employee as well 
    month = models.CharField(max_length=30)
    date_range = models.CharField(max_length=300) 
    year = models.CharField(max_length=4) 
    pay_cycle = models.IntegerField() 
    rate = models.FloatField(null=True, blank=True)
    earning_allowance = models.FloatField(null=True, blank=True)
    deductions_tax = models.FloatField(null=True, blank=True)
    deductions_health = models.FloatField(null=True, blank=True)
    pag_ibig = models.FloatField(null=True, blank=True)
    sss = models.FloatField(null=True, blank=True)
    overtime = models.FloatField(null=True, blank=True)
    total_pay = models.FloatField(null=True, blank=True)

    def getIDNumber(self):
        return self.id_number

    def getMonth(self):
        return self.month

    def getDate_range(self):
        return self.date_range

    def getYear(self):
        return self.year

    def getPay_cycle(self):
        return self.pay_cycle

    def getRate(self):
        return self.rate

    def getCycleRate(self):
        return self.rate / 2 if self.rate else 0

    def getEarning_allowance(self):
        return self.earning_allowance

    def getDeductions_tax(self):
        return self.deductions_tax

    def getDeductions_health(self):
        return self.deductions_health

    def getPag_ibig(self):
        return self.pag_ibig

    def getSSS(self):
        return self.sss

    def getOvertime(self):
        return self.overtime

    def getTotal_pay(self):
        return self.total_pay

    def str(self):
        return (f"{self.id_number} | {self.month} {self.date_range}, {self.year} "
                f"(Cycle {self.pay_cycle}) - Total Pay: ₱{self.total_pay:.2f}")

    class Meta:
        ordering = ['year', 'month'] # arranges years and months 