function updatePrice(select) {

    const minutes =
        parseInt(select.value);

    const hourlyRate =
        parseFloat(select.dataset.hourlyRate);

    const price =
        (minutes / 60) * hourlyRate;

    const form =
        select.closest("form");

    const priceElement =
        form.querySelector(".price-value");

    priceElement.textContent =
        "₱" + price.toFixed(2);
}