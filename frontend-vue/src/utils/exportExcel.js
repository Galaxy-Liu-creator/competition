import * as XLSX from 'xlsx'

/**
 * 统一 Excel 导出工具。
 * exportExcel({ filename, sheets: [{ name, columns: [{label, key, width?}], rows }] })
 * - key 支持字符串取值或 (row) => value 函数列
 * - 生成 `<filename>_<YYYY-MM-DD>.xlsx` 并触发浏览器下载
 */
export function exportExcel({ filename, sheets }) {
  const workbook = XLSX.utils.book_new()
  sheets.forEach(({ name, columns, rows }) => {
    const header = columns.map((col) => col.label)
    const body = (rows || []).map((row) =>
      columns.map((col) => {
        const value = typeof col.key === 'function' ? col.key(row) : row[col.key]
        return value ?? ''
      }),
    )
    const sheet = XLSX.utils.aoa_to_sheet([header, ...body])
    sheet['!cols'] = columns.map((col) => ({ wch: col.width || 16 }))
    // Excel 工作表名上限 31 字符
    XLSX.utils.book_append_sheet(workbook, sheet, String(name).slice(0, 31))
  })
  const date = new Date().toISOString().slice(0, 10)
  XLSX.writeFile(workbook, `${filename}_${date}.xlsx`)
}
