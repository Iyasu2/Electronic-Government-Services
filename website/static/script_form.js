const buttonTexts = [
    { text: "Driver's license Renewal", variable: "driver_license_renewal" },
    { text: "New National ID", variable: "national_id_new" },
    { text: "National ID Renewal", variable: "national_id_renewal" },
    { text: "Birth Certificate", variable: "birth_certificate" },
    { text: "Text for Button 5", variable: "button_5" },
  ];
  const container = document.getElementById("button-container");

  for (let i = 0; i < buttonTexts.length; i++) {
    if (i % 2 === 0) {
      const buttonPairDiv = document.createElement("div");
      buttonPairDiv.className = "button-pair";
      container.appendChild(buttonPairDiv);
    }

    const buttonDiv = document.createElement("div");
    buttonDiv.className = "button-wrapper";
    container.lastElementChild.appendChild(buttonDiv);

    const button = document.createElement("button");
    button.textContent = "Apply";
    button.onclick = function () {
      window.location.href = "/form?variable=" + buttonTexts[i].variable;
    };
    buttonDiv.appendChild(button);

    const text = document.createElement("p");
    text.textContent = buttonTexts[i].text;
    buttonDiv.appendChild(text);