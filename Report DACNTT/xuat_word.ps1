# Xuất bản Word của báo cáo từ main.pdf (Word tự chuyển PDF sang .docx).
# Chạy sau khi biên dịch main.pdf:  powershell -ExecutionPolicy Bypass -File xuat_word.ps1
# Kết quả: BaoCao_DACNTT.docx cạnh main.pdf. Cần Microsoft Word trên máy.
# Lưu ý: Word hỏi "sẽ chuyển PDF thành tài liệu chỉnh sửa được" và DisplayAlerts không tắt được hộp thoại này,
# nên khi chạy ẩn script sẽ treo. Trước lần chạy đầu, tắt hộp thoại một lần cho tài khoản Windows:
#   reg add HKCU\Software\Microsoft\Office\16.0\Word\Options /v DisableConvertPdfWarning /t REG_DWORD /d 1 /f
param([string]$Pdf = "main.pdf", [string]$Docx = "BaoCao_DACNTT.docx")
$ErrorActionPreference = "Stop"
$goc = Split-Path -Parent $MyInvocation.MyCommand.Path
$pdfPath = Join-Path $goc $Pdf
$docxPath = Join-Path $goc $Docx
if (-not (Test-Path $pdfPath)) { throw "Không thấy $pdfPath, hãy biên dịch báo cáo trước." }

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    # ConfirmConversions = $false: không hỏi lại khi mở PDF
    $doc = $word.Documents.Open($pdfPath, $false, $true)
    $doc.SaveAs2($docxPath, 16)   # 16 = wdFormatDocumentDefault (.docx)
    $trang = $doc.ComputeStatistics(2)  # 2 = wdStatisticPages
    $doc.Close($false)
    "Đã ghi $docxPath ($trang trang)"
}
finally {
    $word.Quit()
}
