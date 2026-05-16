document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("post-container");
  const csrfToken = document.querySelector(
    '[name="csrfmiddlewaretoken"]',
  )?.value;

  // fetching data
  let state = {
    page: 2,
    currentGroupId: null,
    emptyPage: false,
    blockRequest: false,
  };

  const loadPosts = (isNewGroup = false) => {
    if (state.emptyPage || state.blockRequest) return;
    state.blockRequest = true;

    let url = `?page=${state.page}`;
    if (state.currentGroupId) url += `&group_id=${state.currentGroupId}`;

    fetch(url, {
      headers: { "x-requested-with": "XMLHttpRequest" },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.html.trim() === "") {
          state.emptyPage = true;
        } else {
          if (isNewGroup) container.innerHTML = data.html;
          else container.insertAdjacentHTML("beforeend", data.html);

          state.blockRequest = false;
          state.page += 1;
          if (!data.has_next) state.emptyPage = true;
        }
      });
  };

  // for fetching filtered community(e.g fun, sports)
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => {
      state.page = 1;
      state.emptyPage = false;
      state.blockRequest = false;
      state.currentGroupId = item.dataset.communityId;
      loadPosts(true);

      document.querySelectorAll(".nav-item").forEach((i) => {
        i.classList.remove("active");
      });

      item.classList.add("active");
    });
  });

  // infinite scroll
  window.onscroll = () => {
    let margin =
      document.body.offsetHeight - (window.innerHeight + window.pageYOffset);
    if (margin < 200) loadPosts(false);
  };

  // Mobile-phone hide and show logic
  document.getElementById("toggle-sidebar").addEventListener("click", () => {
    document.getElementById("sidebar").classList.toggle("show");
  });

  // form creating, hiding and showing loigic
  const wrapper = document.querySelector(".form-wrapper");
  const content = document.querySelector(".form-content");
  const tagContainer = document.getElementById("tag_filter");

  document.getElementById("open-form")?.addEventListener("click", () => {
    fetch("check_auth")
      .then((res) => res.json())
      .then((data) => {
        if (data.is_authenticated) {
          wrapper.classList.add("show");

          wrapper.addEventListener("click", () => {
            wrapper.classList.remove("show");
          });

          document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && wrapper.classList.contains("show")) {
              wrapper.classList.remove("show");
            }
          });

          // for filtering tag
          let tagList = [];
          document.querySelector("#tags").addEventListener("change", (e) => {
            const selectedTagName = e.target.value;

            if (
              selectedTagName === "none" ||
              tagList.includes(selectedTagName)
            ) {
              e.target.value = "none";
              return;
            }

            tagList.push(selectedTagName);

            const li = document.createElement("li");
            li.id = `tag-${encodeURIComponent(selectedTagName)}`;
            li.classList.add("tag-pill");

            const textSpan = document.createElement("span");
            textSpan.textContent = selectedTagName;
            li.appendChild(textSpan);

            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "×";

            deleteBtn.addEventListener("click", () => {
              tagList = tagList.filter((item) => item !== selectedTagName);
              li.remove();
            });

            li.appendChild(deleteBtn);
            tagContainer.appendChild(li);

            e.target.value = "none";
          });

          content.addEventListener("click", (e) => {
            e.stopPropagation();
          });

          // placeholder for creating post
          const createPost = (content) => {
            fetch("/create-post-url/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
              },
              body: JSON.stringify({
                content: content,
                group: state.currentGroupId,
              }),
            })
              .then((res) => res.json())
              .then((data) => {
                wrapper.classList.remove("show");
                console.log("Success");
              })
              .catch((err) => console.error("Error", err));
          };
        } else {
          console.log("Not registered");
          window.location.href = logInUrl;
        }
      });
  });
});
