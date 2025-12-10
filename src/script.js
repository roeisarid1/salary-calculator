const calcBtn = document.getElementById("calcBtn");
const resultBox = document.getElementById("result");

async function sendCalc() {
  const salary = document.getElementById("salary").value;
  const file = document.getElementById("file").files[0];

  if (!salary || !file) {
    resultBox.innerText = "❌ מלא את כל השדות";
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
  } catch {
    resultBox.innerText = "⚠️ שגיאה בחישוב";
    resultBox.className = "error";
  }
}

calcBtn.addEventListener("click", sendCalc);
