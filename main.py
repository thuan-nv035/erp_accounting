import uvicorn
from fastapi import FastAPI
from database import Base, engine
from routers import account, journal, ledger, report, customer, supplier, product, sales_invoice

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Accounting ERP API",
    description="Hệ thống kế toán bằng Python FastAPI",
    version="1.0.0"
)

app.include_router(account.router)
app.include_router(journal.router)
app.include_router(ledger.router)
app.include_router(report.router)
app.include_router(customer.router)
app.include_router(supplier.router)
app.include_router(product.router)
app.include_router(sales_invoice.router)

@app.get("/")
def root():
    return {
        "message": "Accounting API is running"
    }

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)