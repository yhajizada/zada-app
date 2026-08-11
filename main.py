from datetime import date, datetime, timedelta
import csv
import io
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()
app = FastAPI(title="ZADA Enterprise Ultimate ERP & Tax API", version="10.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GENİŞLƏNDİRİLMİŞ BAZALAR ---
fake_transactions = []
fake_debts = []
fake_inventory = [
    {"id": 1, "name": "MacBook Pro M3 Max", "quantity": 12, "buy_price": 4200.0, "sell_price": 5400.0, "category": "Elektronika"},
    {"id": 2, "name": "Erqonomik Ofis Kreslosu", "quantity": 25, "buy_price": 180.0, "sell_price": 320.0, "category": "Mebel"}
]
fake_damaged_goods = [
    {"id": 1, "name": "Zədələnmiş Monitor 27'", "quantity": 2, "loss_amount": 700.0, "reason": "Daşınma zamanı qırılıb", "date": "2026-08-05"}
]
fake_accounts = [
    {"id": 1, "name": "Əsas Nağd Kassa", "balance": 14200.0, "currency": "₼"},
    {"id": 2, "name": "Kapital Bank (Biznes Hesab)", "balance": 68500.0, "currency": "₼"},
    {"id": 3, "name": "Unibank Valyuta Hesabı", "balance": 12400.0, "currency": "$"}
]
fake_employees = [
    {"id": 1, "name": "Elvin Məmmədov", "position": "Baş Anbardar", "salary": 950.0, "status": "Ödənilib"},
    {"id": 2, "name": "Leyla Əliyeva", "position": "Satış Meneceri", "salary": 1300.0, "status": "Gözləmədə"},
    {"id": 3, "name": "Orxan Quliyev", "position": "DevOps Mühəndis", "salary": 2200.0, "status": "Ödənilib"},
    {"id": 4, "name": "Nigar Həsənova", "position": "Baş Mühasib", "salary": 1800.0, "status": "Gözləmədə"}
]
fake_crm = [
    {"id": 1, "name": "MegaStore MMC", "type": "Təchizatçı", "phone": "+994 50 123 45 67", "balance": 0.0},
    {"id": 2, "name": "Baku Retail Group", "type": "Müştəri", "phone": "+994 55 987 65 43", "balance": 1250.0}
]
fake_invoices = [
    {"id": 1, "invoice_number": "E-Q-2026-101", "counterparty": "Baku Retail Group", "amount": 3540.0, "vat_included": True, "status": "Təqdim edildi", "date": "2026-08-10"}
]
fake_audit_logs = [
    {"id": 1, "action": "ZADA Enterprise v10.0 Pro sistemi uğurla işə salındı", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
]

user_subscription = {
    "company_name": "ZADA Enterprise Ultimate MMC",
    "voen": "1402938471",
    "tax_system": "ƏDV Ödəyicisi (18%) / Sadələşdirilmiş Vergi Rejimi",
    "plan": "Global Unlimited Tax & ERP Pro",
    "status": "active",
    "expires_at": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d")
}

# --- PYDANTIC MODELLƏRİ ---
class TransactionCreate(BaseModel):
    amount: float
    type: str  # "income" / "expense"
    category: str
    description: Optional[str] = None
    date: date

class DebtCreate(BaseModel):
    customer_name: str
    amount: float
    status: str = "pending"
    due_date: Optional[date] = None

class ProductCreate(BaseModel):
    name: str
    quantity: int
    buy_price: float
    sell_price: float
    category: str = "Ümumi"

class DamagedGoodCreate(BaseModel):
    name: str
    quantity: int
    loss_amount: float
    reason: str
    date: date

class EmployeeCreate(BaseModel):
    name: str
    position: str
    salary: float
    status: str = "Gözləmədə"

class CrmCreate(BaseModel):
    name: str
    type: str
    phone: str
    balance: float = 0.0

class InvoiceCreate(BaseModel):
    invoice_number: str
    counterparty: str
    amount: float
    vat_included: bool = True
    date: date

# --- ENDPOINTLƏR ---
from fastapi.responses import HTMLResponse
import os

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join("templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return {"message": "ZADA Enterprise Ultimate v10.0 Pro tam gücü ilə işləyir!"}

@app.get("/api/accounts/")
def get_accounts():
    return fake_accounts

@app.get("/api/transactions/")
def get_transactions():
    return fake_transactions

@app.post("/api/transactions/")
def create_transaction(t: TransactionCreate):
    new_item = {"id": len(fake_transactions) + 1, **t.dict()}
    fake_transactions.append(new_item)
    fake_audit_logs.insert(0, {"id": len(fake_audit_logs)+1, "action": f"Maliyyə əməliyyatı: {t.amount} ₼ ({t.category})", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return new_item

@app.get("/api/debts/")
def get_debts():
    return fake_debts

@app.post("/api/debts/")
def create_debt(d: DebtCreate):
    new_item = {"id": len(fake_debts) + 1, **d.dict()}
    fake_debts.append(new_item)
    return new_item

@app.put("/api/debts/{debt_id}")
def update_debt(debt_id: int, status: str):
    for debt in fake_debts:
        if debt["id"] == debt_id:
            debt["status"] = status
            return {"message": "Borc statusu yeniləndi", "debt": debt}
    raise HTTPException(status_code=404, detail="Borc tapılmadı")

@app.get("/api/products/")
def get_products():
    return fake_inventory

@app.post("/api/products/")
def create_product(p: ProductCreate):
    new_item = {"id": len(fake_inventory) + 1, **p.dict()}
    fake_inventory.append(new_item)
    fake_audit_logs.insert(0, {"id": len(fake_audit_logs)+1, "action": f"Anbara məhsul əlavə edildi: {p.name} ({p.quantity} ədəd)", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return new_item

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    global fake_inventory
    fake_inventory = [p for p in fake_inventory if p["id"] != product_id]
    return {"message": "Məhsul anbardan silindi"}

# Xarab / Yararsız Mal (Adxot) Endپوینتləri
@app.get("/api/damaged-goods/")
def get_damaged_goods():
    return fake_damaged_goods

@app.post("/api/damaged-goods/")
def create_damaged_good(dg: DamagedGoodCreate):
    new_item = {"id": len(fake_damaged_goods) + 1, **dg.dict()}
    fake_damaged_goods.append(new_item)
    fake_audit_logs.insert(0, {"id": len(fake_audit_logs)+1, "action": f"Yararsız mal silindi (Adxot): {dg.name} - Zərər: {dg.loss_amount} ₼", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return new_item

@app.get("/api/employees/")
def get_employees():
    return fake_employees

@app.post("/api/employees/")
def create_employee(e: EmployeeCreate):
    new_item = {"id": len(fake_employees) + 1, **e.dict()}
    fake_employees.append(new_item)
    return new_item

@app.put("/api/employees/{emp_id}")
def pay_employee(emp_id: int):
    for emp in fake_employees:
        if emp["id"] == emp_id:
            emp["status"] = "Ödənilib"
            fake_audit_logs.insert(0, {"id": len(fake_audit_logs)+1, "action": f"Maaş ödənildi: {emp['name']} ({emp['salary']} ₼)", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            return {"message": "Maaş ödənildi", "employee": emp}
    raise HTTPException(status_code=404, detail="İşçi tapılmadı")

@app.get("/api/crm/")
def get_crm():
    return fake_crm

@app.post("/api/crm/")
def create_crm(c: CrmCreate):
    new_item = {"id": len(fake_crm) + 1, **c.dict()}
    fake_crm.append(new_item)
    return new_item

@app.get("/api/invoices/")
def get_invoices():
    return fake_invoices

@app.post("/api/invoices/")
def create_invoice(inv: InvoiceCreate):
    new_item = {"id": len(fake_invoices) + 1, "status": "Təqdim edildi", **inv.dict()}
    fake_invoices.append(new_item)
    fake_audit_logs.insert(0, {"id": len(fake_audit_logs)+1, "action": f"E-Qaimə yaradıldı: {inv.invoice_number} ({inv.amount} ₼)", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    return new_item

@app.get("/api/logs/")
def get_logs():
    return fake_audit_logs[:15]

@app.get("/api/subscription")
def get_subscription():
    return user_subscription

# --- GELİŞMİŞ VERGİ, ƏDV VƏ AI ANALİZ MOTORU ---
@app.get("/api/stats/detailed")
def get_detailed_stats(lang: str = "az"):
    total_income = sum(t["amount"] for t in fake_transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in fake_transactions if t["type"] == "expense")
    
    # Əlavə olaraq xarab malların zərəri xərclərə əlavə olunur
    total_damaged_loss = sum(dg["loss_amount"] for dg in fake_damaged_goods)
    total_expense_with_loss = total_expense + total_damaged_loss
    
    net_balance = total_income - total_expense_with_loss
    
    # Azərbaycan Vergi Məcəlləsi Hesablamaları
    estimated_vat = total_income * 0.18 / 1.18 if total_income > 0 else 0.0
    estimated_simplified_tax = total_income * 0.02
    gross_profit = total_income - total_expense_with_loss
    estimated_profit_tax = gross_profit * 0.20 if gross_profit > 0 else 0.0

    total_pending_debt = sum(d["amount"] for d in fake_debts if d["status"] == "pending")
    total_inventory_value = sum(p["quantity"] * p["buy_price"] for p in fake_inventory)
    potential_inventory_profit = sum(p["quantity"] * (p["sell_price"] - p["buy_price"]) for p in fake_inventory)
    total_accounts_balance = sum(acc["balance"] for acc in fake_accounts)
    total_payroll = sum(e["salary"] for e in fake_employees)

    advices = {
        "az": {
            "stable": "Sistem göstəriciləriniz mükəmməldir. Anbar dövriyyəsi və ƏDV balansınız qanunvericiliyə tam uyğundur.",
            "danger": "Diqqət! Xarab mal (adxot) və xərclər artmaqdadır. Anbar optimizasiyası edilməsi şiddətlə tövsiyə olunur.",
            "tax_note": f"Cari dövriyyəyə əsasən hesablanmış ƏDV: {estimated_vat:.2f} ₼ | Mənfəət Vergisi: {estimated_profit_tax:.2f} ₼"
        },
        "en": {
            "stable": "Your system metrics are optimal. Inventory turnover and VAT balances comply with local regulations.",
            "danger": "Warning! Damaged goods and expenses are rising. Immediate inventory review is recommended.",
            "tax_note": f"Estimated VAT based on turnover: {estimated_vat:.2f} ₼ | Profit Tax: {estimated_profit_tax:.2f} ₼"
        },
        "ru": {
            "stable": "Ваши системные показатели в норме. Оборот склада и баланс НДС соответствуют законодательству.",
            "danger": "Внимание! Растут расходы и потери по браку. Рекомендуется оптимизация склада.",
            "tax_note": f"Расчетный НДС: {estimated_vat:.2f} ₼ | Налог на прибыль: {estimated_profit_tax:.2f} ₼"
        }
    }

    lang_key = lang if lang in advices else "az"
    ai_advice = advices[lang_key]["stable"]
    if total_expense_with_loss > total_income and total_income > 0:
        ai_advice = advices[lang_key]["danger"]

    return {
        "total_income": total_income,
        "total_expense": total_expense_with_loss,
        "total_damaged_loss": total_damaged_loss,
        "net_balance": net_balance,
        "estimated_vat": estimated_vat,
        "estimated_simplified_tax": estimated_simplified_tax,
        "estimated_profit_tax": estimated_profit_tax,
        "total_pending_debt": total_pending_debt,
        "total_inventory_value": total_inventory_value,
        "potential_inventory_profit": potential_inventory_profit,
        "total_accounts_balance": total_accounts_balance,
        "total_payroll": total_payroll,
        "ai_advice": ai_advice,
        "tax_note": advices[lang_key]["tax_note"]
    }

@app.get("/api/export/full-report")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ZADA ENTERPRISE ULTIMATE - FINANSAL VE VERGI HESABATI"])
    writer.writerow(["ID", "Mebleg", "Nov", "Kateqoriya", "Tarix"])
    for t in fake_transactions:
        writer.writerow([t["id"], t["amount"], t["type"], t["category"], t["date"]])
    
    writer.writerow([])
    writer.writerow(["XARAB / YARARSIZ MALLAR (ADXOT)"])
    writer.writerow(["ID", "Mehsul", "Miqdar", "Zerer Meblegi", "Sebeb", "Tarix"])
    for dg in fake_damaged_goods:
        writer.writerow([dg["id"], dg["name"], dg["quantity"], dg["loss_amount"], dg["reason"], dg["date"]])

    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=zada_enterprise_ultimate_report.csv"})