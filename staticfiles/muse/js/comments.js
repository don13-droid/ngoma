// static/js/comments.js

(function () {
  // CSRF (Django): read cookie
  function getCookie(name) {
    const cookieStr = document.cookie;
    if (!cookieStr) return null;
    const cookies = cookieStr.split(";").map(c => c.trim());
    for (const c of cookies) {
      if (c.startsWith(name + "=")) return decodeURIComponent(c.split("=")[1]);
    }
    return null;
  }
  const csrftoken = getCookie("csrftoken");

  const section = document.getElementById("comments-section");
  if (!section) return;

  const postId = section.getAttribute("data-post-id");
  const addUrl = `/posts/${postId}/comments/add/`;

  const commentsList = document.getElementById("comments-list");
  const newCommentForm = document.getElementById("new-comment-form");

  // Toggle reply forms
  section.addEventListener("click", (e) => {
    const btn = e.target.closest(".reply-toggle");
    if (btn) {
      const targetId = btn.getAttribute("data-target");
      const form = document.getElementById(targetId);
      if (form) form.style.display = form.style.display === "block" ? "none" : "block";
    }
  });

  // Submit new root comment
  if (newCommentForm) {
    newCommentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(newCommentForm);
      formData.append("parent_id", ""); // root

      const res = await fetch(addUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: formData
      });

      if (!res.ok) {
        alert("Could not post comment.");
        return;
      }
      const data = await res.json();
      const node = buildCommentNode(data);
      // Prepend newest on top (or append — your choice)
      commentsList.prepend(node);
      newCommentForm.reset();
    });
  }

  // Delegate reply form submissions
  section.addEventListener("submit", async (e) => {
    const form = e.target.closest(".reply-form");
    if (!form) return;
    e.preventDefault();

    const parentId = form.getAttribute("data-parent-id");
    const formData = new FormData(form);
    formData.append("parent_id", parentId);

    const res = await fetch(addUrl, {
      method: "POST",
      headers: { "X-CSRFToken": csrftoken },
      body: formData
    });

    if (!res.ok) {
      alert("Could not post reply.");
      return;
    }
    const data = await res.json();
    const replyNode = buildCommentNode(data);

    const repliesContainer = document.getElementById(`replies-for-${parentId}`);
    if (repliesContainer) {
      repliesContainer.appendChild(replyNode);
    }
    form.reset();
    form.style.display = "none";
  });

  // Build a comment DOM node from JSON
  function buildCommentNode(data) {
    const wrapper = document.createElement("div");
    wrapper.className = "comment";
    wrapper.id = `comment-${data.id}`;
    wrapper.setAttribute("data-comment-id", data.id);

    wrapper.innerHTML = `
      <div class="meta">
        <strong>${escapeHtml(data.author_name)}</strong> • <span>${escapeHtml(data.created_at)}</span>
      </div>
      <div class="content">${nl2br(escapeHtml(data.content))}</div>
      <div class="actions">
        <button class="reply-toggle" data-target="reply-form-${data.id}">Reply</button>
      </div>
      <form class="reply-form" id="reply-form-${data.id}" data-parent-id="${data.id}" style="display:none;">
        ${csrfHiddenInput()}
        ${maybeAnonNameInput()}
        <textarea name="content" rows="2" placeholder="Write a reply..." required></textarea>
        <button type="submit">Reply</button>
      </form>
      <div class="replies" id="replies-for-${data.id}"></div>
    `;
    return wrapper;
  }

  // Utilities
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function nl2br(str) {
    return str.replace(/\n/g, "<br>");
  }

  // When using fetch + CSRF cookie, you don't strictly need hidden input,
  // but including it keeps parity with Django templates if desired.
  function csrfHiddenInput() {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
    if (!token) return "";
    return `<input type="hidden" name="csrfmiddlewaretoken" value="${token}">`;
  }

  // Only render the anonymous name input if the page lacks an authenticated context.
  function maybeAnonNameInput() {
    // Heuristic: if the top form has an author_name input, assume anon allowed
    const anonField = document.querySelector('#new-comment-form input[name="author_name"]');
    if (!anonField) return "";
    return `<input type="text" name="author_name" placeholder="Your name (optional)" />`;
  }
})();
