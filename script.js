const calcBtn = document.getElementById("calcBtn");
const calcAndSaveBtn = document.getElementById("calcAndSaveBtn");
const exportCsvBtn = document.getElementById("exportCsvBtn");
const resultBox = document.getElementById("result");

const monthSelect = document.getElementById("monthSelect");
const yearInput = document.getElementById("yearInput");
const chartYearSelect = document.getElementById("chartYearSelect");

const LS_KEY = "salary_history_v1";

// אתחול ברירת מחדל + מילוי רשימת שנים לגרף
document.addEventListener("DOMContentLoaded", () => {
  const now = new Date();
  if (!monthSelect.value) monthSelect.value = String(now.getMonth() + 1);
  if (!yearInput.value) yearInput.value = String(now.getFullYear());

  populateChartYearOptions();
  drawSalaryChart(Number(chartYearSelect.value || now.getFullYear()));
});

// ------- LocalStorage helpers -------
function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) || "[]");
  } catch {
    return [];
  }
}
function saveHistory(arr) {
  localStorage.setItem(LS_KEY, JSON.stringify(arr));
}
function addEntryToHistory(entry) {
  const hist = loadHistory();
  hist.push(entry);
  saveHistory(hist);
}

// כל השנים שקיימות בהיסטוריה
function getYearsInHistory() {
  const hist = loadHistory();
  const years = new Set(hist.map((r) => Number(r.year)));
  return Array.from(years)
    .filter(Boolean)
    .sort((a, b) => a - b);
}

// מילוי אפשרויות בחירת שנה לגרף
function populateChartYearOptions() {
  const nowYear = new Date().getFullYear();
  let years = getYearsInHistory();
  if (!years.length) years = [nowYear];
  chartYearSelect.innerHTML = years
    .map((y) => `<option value="${y}">${y}</option>`)
    .join("");
  const entryYear = Number(yearInput.value || nowYear);
  if (!years.includes(entryYear)) {
    chartYearSelect.insertAdjacentHTML(
      "beforeend",
      `<option value="${entryYear}">${entryYear}</option>`
    );
  }
  chartYearSelect.value = String(entryYear);
}

// סיכום חודשי לפי שנה
function monthlySummaryByYear(year) {
  const hist = loadHistory().filter((r) => Number(r.year) === Number(year));
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  return months.map((m) => {
    const rows = hist.filter((r) => Number(r.month) === m);
    const total = rows.reduce((acc, r) => acc + Number(r.total_salary || 0), 0);
    return { month: m, total_salary: total };
  });
}

// ייצוא CSV
function exportCsv() {
  const rows = loadHistory();
  if (!rows.length) {
    alert("אין נתונים בהיסטוריה");
    return;
  }
  const headers = [
    "calc_ts",
    "year",
    "month",
    "source_file",
    "hourly_rate",
    "total_salary",
    "regular_hours",
    "night_hours",
    "vacation_days",
    "travel_refund_total",
  ];
  const csv = [
    headers.join(","),
    ...rows.map((r) => headers.map((h) => r[h] ?? "").join(",")),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "salary_history.csv";
  a.click();
  URL.revokeObjectURL(url);
}

// ------- גרף עמודות צבעוני -------
if (window.ChartDataLabels) Chart.register(ChartDataLabels);

let _chart;
function formatCurrency(v) {
  return (
    Number(v || 0).toLocaleString("he-IL", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }) + " ₪"
  );
}
function drawSalaryChart(year) {
  const data = monthlySummaryByYear(year);
  const labels = data.map((r) => String(r.month).padStart(2, "0"));
  const totals = data.map((r) => r.total_salary);
  const ctx = document.getElementById("salaryChart").getContext("2d");
  if (_chart) _chart.destroy();

  const gradients = totals.map((_, i) => {
    const g = ctx.createLinearGradient(0, 0, 0, 300);
    const palette = [
      ["#7C3AED", "#C084FC"],
      ["#10B981", "#6EE7B7"],
      ["#F59E0B", "#FCD34D"],
      ["#3B82F6", "#93C5FD"],
      ["#EF4444", "#FCA5A5"],
      ["#06B6D4", "#67E8F9"],
      ["#A855F7", "#D8B4FE"],
      ["#22C55E", "#86EFAC"],
      ["#F97316", "#FDBA74"],
      ["#EAB308", "#FDE047"],
      ["#FB7185", "#FBCFE8"],
      ["#6366F1", "#A5B4FC"],
    ];
    const [c1, c2] = palette[i % palette.length];
    g.addColorStop(0, c1);
    g.addColorStop(1, c2);
    return g;
  });

  _chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: `שכר חודשי (₪) — ${year}`,
          data: totals,
          backgroundColor: gradients,
          borderRadius: 14,
          barThickness: 44,
          maxBarThickness: 60,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 900, easing: "easeOutQuart" },
      layout: { padding: { top: 10, right: 8, bottom: 8, left: 8 } },
      plugins: {
        title: {
          display: true,
          text: "הכנסה חודשית לפי שנה",
          font: { size: 18, weight: "700" },
        },
        legend: { display: false },
        tooltip: {
          usePointStyle: true,
          callbacks: {
            title: (items) => `חודש ${items[0].label}`,
            label: (ctx) => " " + formatCurrency(ctx.parsed.y),
          },
        },
        datalabels: {
          anchor: "end",
          align: "end",
          offset: 6,
          formatter: (v) => formatCurrency(v),
          color: "#111827",
          font: { weight: "700", size: 12 },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "חודש" },
          grid: { display: false },
          ticks: { font: { size: 12 } },
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: "שכר (₪)" },
          ticks: { callback: (val) => formatCurrency(val), font: { size: 12 } },
          grid: {
            color: (ctx) =>
              ctx.tick.value === 0 ? "rgba(0,0,0,0.2)" : "rgba(0,0,0,0.06)",
          },
        },
      },
    },
  });
}

// ------- שליחת חישוב ל-API -------
async function sendCalc({ save = false } = {}) {
  const salary = document.getElementById("salary").value;
  const file = document.getElementById("file").files[0];

  if (!salary || !file) {
    resultBox.innerText = "❌ מלא את כל השדות";
    resultBox.className = "error";
    return;
  }

  const month = Number(monthSelect.value);
  const year = Number(yearInput.value);
  if (!(month >= 1 && month <= 12) || !(year >= 2000 && year <= 2100)) {
    resultBox.innerText = "⚠️ בחר חודש/שנה תקינים";
    resultBox.className = "error";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("salary", salary);

  try {
    const response = await fetch("http://127.0.0.1:8000/calc", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    resultBox.innerHTML = `
      ✅ שכר כולל: ${(data.total_salary ?? 0).toFixed(2)} ₪<br>
      🕒 שעות רגילות: ${(data.regular_hours ?? 0).toFixed(2)}<br>
      🌙 שעות לילה/סופ"ש: ${(data.night_hours ?? 0).toFixed(2)}<br>
      🏖️ ימי חופשה: ${data.vacation_days ?? 0}<br>
      🚗 החזר נסיעות: ${data.travel_refund_total ?? 0} ₪
    `;
    resultBox.className = "success";

    if (save) {
      const now = new Date();
      const entry = {
        calc_ts: now.toISOString().slice(0, 19),
        year,
        month,
        source_file: file.name,
        hourly_rate: Number(salary),
        total_salary: Number(data.total_salary || 0),
        regular_hours: Number(data.regular_hours || 0),
        night_hours: Number(data.night_hours || 0),
        vacation_days: Number(data.vacation_days || 0),
        travel_refund_total: Number(data.travel_refund_total || 0),
      };
      addEntryToHistory(entry);
      populateChartYearOptions();
      drawSalaryChart(Number(chartYearSelect.value || year));
    }
  } catch {
    resultBox.innerText = "⚠️ שגיאה בחישוב";
    resultBox.className = "error";
  }
}

calcBtn.addEventListener("click", () => sendCalc({ save: false }));
calcAndSaveBtn?.addEventListener("click", () => sendCalc({ save: true }));
exportCsvBtn?.addEventListener("click", exportCsv);
chartYearSelect?.addEventListener("change", () =>
  drawSalaryChart(Number(chartYearSelect.value))
);
