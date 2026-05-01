document.addEventListener("DOMContentLoaded", () => {
    let page = 1;
    let emptyPage = false;
    let blockRequest = false;

    window.onscroll = () => {
        // Check whether we are at bottom of page or not
        let margin = document.body.offsetHeight - (window.innerHeight + window.pageYOffset)

        if (margin < 200 && !emptyPage && !blockRequest) {
            blockRequest = true;
            page += 1;

            fetch(`?page=${page}`, {
                headers: {
                    "x-requested-with": "XMLHttpRequest"
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.html.trim() === "") {
                        emptyPage = true;
                    }
                    else {
                        // Append new data
                        const container = document.getElementById("post-container");
                        container.insertAdjacentHTML("beforeend", data.html);

                        blockRequest = false;

                        if (!data.has_next) {
                            empty.page = true;
                        }
                    }
                })
                .catch(error => console.error("Error loading posts", error));
        }
    }
});
