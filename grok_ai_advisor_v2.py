from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
import datetime

wb = Workbook()
wb.remove(wb.active)

# Constants
TOTAL_CAPITAL = 2100000

tickers = ["JEPI", "SCHD", "JEPQ", "VIG", "SGOV", "NVDY", "ULTY", "CHPY", "MRNY", "YMAX"]
targets = {t: {"pct": v["target_pct"]/100, "amt": v["amount"]} for t, v in {
    "JEPI": {"target_pct": 42.9, "amount": 900000},
    "SCHD": {"target_pct": 23.8, "amount": 500000},
    "JEPQ": {"target_pct": 14.3, "amount": 300000},
    "VIG": {"target_pct": 6.7, "amount": 140000},
    "SGOV": {"target_pct": 2.9, "amount": 60000},
    "NVDY": {"target_pct": 1.19, "amount": 25000},
    "ULTY": {"target_pct": 1.19, "amount": 25000},
    "CHPY": {"target_pct": 0.95, "amount": 20000},
    "MRNY": {"target_pct": 0.71, "amount": 15000},
    "YMAX": {"target_pct": 0.71, "amount": 15000},
}.items()}

payout_data = {
    "JEPI": {"freq": "Monthly", "yield": 0.084},
    "JEPQ": {"freq": "Monthly", "yield": 0.103},
    "SCHD": {"freq": "Quarterly", "yield": 0.033},
    "VIG": {"freq": "Quarterly", "yield": 0.016},
    "SGOV": {"freq": "Monthly", "yield": 0.045},
    "NVDY": {"freq": "Weekly", "yield": 0.60},
    "ULTY": {"freq": "Weekly", "yield": 0.65},
    "CHPY": {"freq": "Weekly", "yield": 0.46},
    "MRNY": {"freq": "Weekly", "yield": 0.71},
    "YMAX": {"freq": "Weekly", "yield": 0.57},
}
category_map = {**{"JEPI": "Core Stable Income", "JEPQ": "Core Stable Income"}, **dict.fromkeys(["SCHD","VIG"], "Quality Dividend Growth"), "SGOV": "Cash Buffer", **dict.fromkeys(["NVDY","ULTY","CHPY","MRNY","YMAX"], "Aggressive High-Yield")}

# Main Portfolio Sheet
ws = wb.create_sheet("Portfolio Overview")
ws.title = "Portfolio Overview"

# Title
ws['A1'] = "🚀 Grok AI Investment Advisor v2"
ws['A1'].font = Font(bold=True, size=18, color="FFFFFF")
ws.merge_cells('A1:M1')
ws['A1'].fill = PatternFill("solid", fgColor="1f6feb")

ws['A3'] = "Total Target Capital"
ws['B3'] = TOTAL_CAPITAL
ws['B3'].number_format = '$#,##0'

ws['A4'] = "Last Updated"
ws['B4'] = datetime.datetime.now().strftime("%Y-%m-%d")

headers = ["Ticker", "Category", "Target %", "Target $", "Live Price (GOOGLEFINANCE)", "Shares", "Current Value", "Current %", "Drift", "Annual Yield", "Est Annual $", "Est Monthly $", "Frequency"]
for c, h in enumerate(headers, 1):
    cell = ws.cell(6, c, h)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="366092")
    cell.alignment = Alignment(horizontal="center")

row = 7
for t in tickers:
    ws.cell(row, 1, t)
    ws.cell(row, 2, category_map[t])
    ws.cell(row, 3, targets[t]["pct"])
    ws.cell(row, 3).number_format = "0.0%"
    ws.cell(row, 4, targets[t]["amt"])
    ws.cell(row, 4).number_format = '$#,##0'
    
    # Price
    ws.cell(row, 5, f'=IFERROR(GOOGLEFINANCE("{t}","price"), 25)')
    
    # Shares
    ws.cell(row, 6, f'=D{row}/E{row}')
    ws.cell(row, 6).number_format = '#,##0.00'
    
    # Value
    ws.cell(row, 7, f'=E{row}*F{row}')
    ws.cell(row, 7).number_format = '$#,##0'
    
    # Current %
    ws.cell(row, 8, f'=G{row}/$B$3')
    ws.cell(row, 8).number_format = "0.0%"
    
    # Drift
    ws.cell(row, 9, f'=H{row}-C{row}')
    ws.cell(row, 9).number_format = "+0.0%;-0.0%"
    
    # Yield
    ws.cell(row, 10, payout_data[t]["yield"])
    ws.cell(row, 10).number_format = "0.0%"
    
    # Annual Payout
    ws.cell(row, 11, f'=D{row}*J{row}')
    ws.cell(row, 11).number_format = '$#,##0'
    
    # Monthly
    freq_cell = get_column_letter(13)
    ws.cell(row, 12, f'=IF(OR({freq_cell}{row}="Monthly",{freq_cell}{row}="Weekly"), K{row}/12, K{row}/4)')
    ws.cell(row, 12).number_format = '$#,##0'
    
    ws.cell(row, 13, payout_data[t]["freq"])
    row += 1

# Totals
total_row = row
ws.cell(total_row, 1, "TOTALS")
ws.cell(total_row, 7, f'=SUM(G7:G{total_row-1})')
ws.cell(total_row, 7).number_format = '$#,##0'
ws.cell(total_row, 8, f'=G{total_row}/B3')
ws.cell(total_row, 8).number_format = "0.0%"
ws.cell(total_row, 11, f'=SUM(K7:K{total_row-1})')
ws.cell(total_row, 11).number_format = '$#,##0'
ws.cell(total_row, 12, f'=L{total_row}')
ws.cell(total_row, 12).number_format = '$#,##0'

# Add table
tab = Table(displayName="PortfolioTable", ref=f"A6:M{total_row}")
style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False, showLastColumn=False, showRowStripes=True, showColumnStripes=True)
tab.tableStyleInfo = style
ws.add_table(tab)

# Other sheets placeholders
ws2 = wb.create_sheet("Holdings Tracker")
ws2['A1'] = "High-Yield Tracker - Manual Entry"
ws2['A2'] = "Asset"
ws2['B2'] = "Cost Basis"
# Add more columns similarly

ws3 = wb.create_sheet("Income Projections")
ws3['A1'] = "Income Projections & Tax Estimator"
ws3['A3'] = "Gross Annual"
ws3['B3'] = f'=Portfolio Overview!K{total_row}'

# Save
wb.save("/home/workdir/Jay_Investment_Tracker.xlsx")
print("Excel file created with dynamic formulas for Google Sheets!")
