console.log("Content script loaded!");

// Перевірка вибраного блоку
function checkSelectedBlock() {
    console.log("Running periodic check...");

    // Видалити кнопки з невибраних блоків
    removeButtonsFromUnselectedBlocks();

    // Знайти вибраний блок
    const selectedBlock = document.querySelector(".jipt-selected");
    if (selectedBlock) {
        console.log("Selected block found:", selectedBlock);
        addButtonToBlock(selectedBlock);
    } else {
        console.log("No selected block found.");
    }
}

// Додавання кнопки до блоку
function addButtonToBlock(blockElement) {
    if (blockElement.querySelector(".custom-action-btn")) {
        console.log("Button already exists in this block.");
        return; // Уникаємо дублювання кнопок
    }

    console.log("Adding button to the selected block...");

    // Створення кнопки
    const checkButton = document.createElement("button");
    checkButton.innerText = "Check";
    checkButton.classList.add("custom-action-btn");

    // Стилізація кнопки
    checkButton.style.position = "absolute";
    checkButton.style.top = "5px";
    checkButton.style.right = "5px";
    checkButton.style.background = "#007bff";
    checkButton.style.color = "white";
    checkButton.style.border = "none";
    checkButton.style.padding = "8px";
    checkButton.style.cursor = "pointer";
    checkButton.style.zIndex = "1000";

    // Додаємо кнопку до блоку
    blockElement.style.position = "relative";
    blockElement.appendChild(checkButton);

    // Додавання обробника подій
    checkButton.addEventListener("click", () => {
        const blockText = blockElement.innerText.trim();
        if (blockText) {
            console.log("Text from the block:", blockText);
            sendTextToChatGPT(blockText);
        } else {
            alert("Block is empty!");
        }
    });
}

// Видалення кнопок із невибраних блоків
function removeButtonsFromUnselectedBlocks() {
    console.log("Checking for buttons to remove...");
    const buttons = document.querySelectorAll(".custom-action-btn");

    buttons.forEach((button) => {
        const parentBlock = button.parentElement;
        if (!parentBlock || !parentBlock.classList.contains("jipt-selected")) {
            console.log("Removing button from block:", parentBlock);
            button.remove();
        }
    });
}

// Надсилання тексту до ChatGPT
function sendTextToChatGPT(text) {
    chrome.runtime.sendMessage({ action: "checkText", text }, (response) => {
        if (response.success) {
            console.log("ChatGPT response:", response.result);
            alert("ChatGPT response:\n" + response.result);
        } else {
            console.error("Error from ChatGPT:", response.error);
            alert("Error occurred: " + response.error);
        }
    });
}

// Спостереження за змінами в DOM
function observeSelectedBlockChanges() {
    console.log("Initializing MutationObserver...");

    const observer = new MutationObserver(() => {
        console.log("MutationObserver detected changes...");
        checkSelectedBlock();
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Додатковий періодичний чек
    setInterval(checkSelectedBlock, 2000);
}

// Запуск спостереження
observeSelectedBlockChanges();
