const generateBtn = document.getElementById('generate-btn');
const viewBtn = document.getElementById('view-btn');
const exportBtn = document.getElementById('export-btn');
const allBtn = document.getElementById('all-btn');
const reportIdInput = document.getElementById('report-id-input');
const resultPre = document.getElementById('result');

generateBtn.addEventListener('click', async () => {
    const response = await fetch('/reports/generate');
    if(response.ok) {
        const data = await response.json();
        resultPre.textContent = JSON.stringify(data, null, 2);
    } else {
        resultPre.textContent = "Błąd podczas generowania raportu.";
    }
});

viewBtn.addEventListener('click', async () => {
    const response = await fetch('/reports/view');
    if(response.ok) {
        const data = await response.json();
        resultPre.textContent = JSON.stringify(data, null, 2);
    } else {
        resultPre.textContent = "Błąd podczas pobierania raportów.";
    }
});

exportBtn.addEventListener('click', () => {
    const reportId = reportIdInput.value;
    if(!reportId) {
        resultPre.textContent = "Podaj report_id przed pobraniem CSV.";
        return;
    }
    window.location.href = `/reports/export?report_id=${reportId}`;
});

allBtn.addEventListener('click', () => {
    window.location.href = '/reports/all';
});
document.getElementById('affected-detailed-btn').addEventListener('click', () => {
    window.location.href = '/reports/affected/detailed';
});
