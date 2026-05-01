ducument.addEventListener("DOMContentLoaded", () => {
    let page = 1;
    let emptyPage = false;
    let blockElement = false;

    window.onscroll = () => {
        let margin = document.body.offsetHeight - (window.innerHeight + window.pageYOffset)

        if (margin < 200 && !emptyPage && !blockElement) {
            blockElement = true;
            page += 1;

            fetch(`post/${post_id}/comments/?page=${page}`, {
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
                        const container = document.getElementById("comment_container");
                        container.insertAdjacentHTML("beforeend", data.html);

                        blockElement = false;

                        if (!data.has_next) {
                            emptyPage = true;
                        }
                    }
                })
                .catch(error => console.error("Error occured while loading page", error))
        }
    }
})
