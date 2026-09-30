const form =
    document.getElementById(
        "comicForm"
    );


const button =
    document.getElementById(
        "generateButton"
    );


const loading =
    document.getElementById(
        "loading"
    );

const errorMessage =
    document.getElementById(
        "errorMessage"
    );


if (form) {

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            button.disabled = true;

            button.textContent =
                "Creating Comic...";

            loading.style.display =
                "block";

            errorMessage.hidden = true;
            errorMessage.textContent = "";

            try {
                const response = await fetch(
                    form.action,
                    {
                        method: form.method,
                        body: new FormData(form)
                    }
                );

                if (!response.ok) {
                    const result = await response.json();
                    throw new Error(
                        result.error || "Comic generation failed. Please try again."
                    );
                }

                const comicHtml = await response.text();
                document.open();
                document.write(comicHtml);
                document.close();
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.hidden = false;
            } finally {
                button.disabled = false;
                button.textContent = "Generate My Comic";
                loading.style.display = "none";
            }
        }
    );

}