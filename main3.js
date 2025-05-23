$("#prediction-form").on('submit', async function(e) {
    e.preventDefault();

    let formData = $(this).serializeArray();
    let inputs = {};

    formData.forEach(function(item) {
        if (["age", "hypertension", "heart_disease", "avg_glucose_level", "bmi"].includes(item.name)) {
            inputs[item.name] = parseFloat(item.value);
        } else {
            inputs[item.name] = item.value;
        }
    });

    const payload = {
        inputs: [inputs]
    };

    try {
        const response = await fetch('http://localhost:8000/api/hfp_prediction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = "";

        if (!response.ok) {
            throw new Error(result.error || "Failed to get prediction");
        }

        if (result.predictions && result.predictions.length > 0) {
            const prediction = result.predictions[0];
            const strokeRisk = prediction.stroke_risk_percentage;
            const noStrokeRisk = prediction.no_stroke_risk_percentage;
            const predictedClass = strokeRisk > noStrokeRisk ? "Likely Stroke" : "No Stroke";

            let html = `
                <div class="prediction-card">
                    <h3>Prediction Results</h3>
                    <div class="prediction-item">
                        <span class="label">No Stroke Risk</span>
                        <span class="value">${noStrokeRisk}%</span>
                    </div>
                    <div class="prediction-item">
                        <span class="label">Stroke Risk</span>
                        <span class="value">${strokeRisk}%</span>
                    </div>
                    <div style="margin-top: 10px; font-size: 18px;">
                        <strong>Prediction:</strong> ${predictedClass}
                    </div>
                </div>
            `;
            resultDiv.innerHTML = html;
        } else {
            resultDiv.innerHTML = "<p>No prediction available.</p>";
        }
    } catch (error) {
        document.getElementById("result").innerHTML = `
            <p style='color: red;'>Error: ${error.message}</p>
        `;
        console.error("Prediction error:", error);
    }
});