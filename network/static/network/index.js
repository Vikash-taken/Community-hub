document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("post-container");
  const csrfToken = document.querySelector(
    '[name="csrfmiddlewaretoken"]',
  )?.value;

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

  // placeholder for creating post in future
  const createPost = (content) => {
    fetch("/create-post-url/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({ content: content, group: state.currentGroupId }),
    })
      .then((res) => res.json())
      .then((data) => {});
  };

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

  window.onscroll = () => {
    let margin =
      document.body.offsetHeight - (window.innerHeight + window.pageYOffset);
    if (margin < 200) loadPosts(false);
  };

  document.getElementById("toggle-sidebar").addEventListener("click", () => {
    document.getElementById("sidebar").classList.toggle("show");
  });
});
