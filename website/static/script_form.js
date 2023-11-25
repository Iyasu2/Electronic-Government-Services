const buttonTexts = [
  { text: "Driver's license Renewal", route: "driver_license_renewal" },
  { text: "National ID", route: "national_id" },
  { text: "Birth Certificate", route: "birth_certificate" },
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

  const button = document.createElement("a");
  button.textContent = "Apply";
  button.href = "/form/" + buttonTexts[i].route;
  buttonDiv.appendChild(button);

  const text = document.createElement("p");
  text.textContent = buttonTexts[i].text;
  buttonDiv.appendChild(text);
}
