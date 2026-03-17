const calcBtn = document.getElementById("calcBtn");
const resultBox = document.getElementById("result");

function setLoading(isLoading) {
  calcBtn.disabled = isLoading;
  calcBtn.textContent = isLoading ? "מחשב..." : "חשב";
}

function showError(msg) {
  resultBox.textContent = "❌ " + msg;
  resultBox.className = "error";
}

function showResult(data) {
  resultBox.innerHTML = `
    <div class="result-row">✅ <strong>שכר כולל:</strong> ${(data.total_salary ?? 0).toFixed(2)} ₪</div>
    <div class="result-row">🕒 <strong>שעות רגילות:</strong> ${(data.regular_hours ?? 0).toFixed(2)}</div>
    <div class="result-row">🌙 <strong>שעות לילה/סופ"ש:</strong> ${(data.night_hours ?? 0).toFixed(2)}</div>
    <div class="result-row">🏖️ <strong>ימי חופשה:</strong> ${data.vacation_days ?? 0}</div>
    <div class="result-row">🚗 <strong>החזר נסיעות:</strong> ${data.travel_refund_total ?? 0} ₪</div>
  `;
  resultBox.className = "success";
}

async function sendCalc() {
  const salaryInput = document.getElementById("salary");
  const fileInput = document.getElementById("file");
  const salary = parseFloat(salaryInput.value);
  const file = fileInput.files[0];

  if (!salaryInput.value || isNaN(salary)) {
    showError("יש להזין שכר לשעה");
    return;
  }
  if (salary <= 0) {
    showError("שכר לשעה חייב להיות מספר חיובי");
    return;
  }
  if (!file) {
    showError("יש לבחור קובץ אקסל");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("salary", salary);

  setLoading(true);
  resultBox.className = "";
  resultBox.textContent = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/calc", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.detail ?? "שגיאה בחישוב");
      return;
    }

    showResult(data);
  } catch {
    showError("לא ניתן להתחבר לשרת – ודא שהשרת פועל");
  } finally {
    setLoading(false);
  }
}

calcBtn.addEventListener("click", sendCalc);
