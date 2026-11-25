const STORAGE_KEY_NAME = "vidstream_admin_key";

function getSavedAdminKey() {
    const inputEl = document.getElementById("adminKeyInput");
    const typedKey = inputEl.value.trim();
    if (typedKey !== "") {
        return typedKey;
    }

    const storedKey = sessionStorage.getItem(STORAGE_KEY_NAME);
    if (storedKey !== null && storedKey.trim() !== "") {
        return storedKey.trim();
    }

    return "";
}

function showBanner(messageText, isError) {
    const bannerEl = document.getElementById("statusBanner");
    bannerEl.textContent = messageText;
    bannerEl.classList.remove("hidden");
    bannerEl.classList.remove("success");
    bannerEl.classList.remove("error");

    if (isError) {
        bannerEl.classList.add("error");
    } else {
        bannerEl.classList.add("success");
    }
}

function showLockedLists(messageText) {
    const videoListBox = document.getElementById("adminVideoList");
    const adListBox = document.getElementById("adminAdList");
    videoListBox.innerHTML = "<p class='muted-text'>" + messageText + "</p>";
    adListBox.innerHTML = "<p class='muted-text'>" + messageText + "</p>";
}

async function verifyAndConnectAdmin() {
    const keyVal = document.getElementById("adminKeyInput").value.trim();
    if (keyVal === "") {
        sessionStorage.removeItem(STORAGE_KEY_NAME);
        showBanner("کلید ادمین نمی‌تواند خالی باشد.", true);
        showLockedLists("ابتدا کلید ادمین را وارد کنید.");
        return;
    }

    try {
        const checkRes = await fetch("/videos/admin/all", {
            method: "GET",
            headers: {
                "X-Admin-Key": keyVal
            }
        });

        if (checkRes.status === 401 || checkRes.status === 403) {
            sessionStorage.removeItem(STORAGE_KEY_NAME);
            showBanner("کلید ادمین اشتباه است. دسترسی رد شد.", true);
            showLockedLists("کلید ادمین نامعتبر است.");
            return;
        }

        if (!checkRes.ok) {
            showBanner("خطا در بررسی کلید ادمین از سرور.", true);
            return;
        }

        sessionStorage.setItem(STORAGE_KEY_NAME, keyVal);
        showBanner("اتصال ادمین تایید شد.", false);
        loadAdminVideos();
        loadAdminAds();
    } catch (err) {
        showBanner("عدم ارتباط با سرور هنگام بررسی کلید ادمین.", true);
    }
}

async function deleteVideoItem(videoId) {
    const adminKey = getSavedAdminKey();
    if (adminKey === "") {
        showBanner("ابتدا کلید ادمین را وارد کنید.", true);
        return;
    }

    try {
        const res = await fetch("/videos/" + videoId, {
            method: "DELETE",
            headers: {
                "X-Admin-Key": adminKey
            }
        });

        if (!res.ok) {
            const errData = await res.json();
            showBanner("خطا در حذف ویدیو: " + (errData.detail || res.status), true);
            return;
        }

        showBanner("ویدیو با موفقیت حذف شد.", false);
        loadAdminVideos();
    } catch (err) {
        showBanner("خطا در ارتباط با سرور هنگام حذف ویدیو.", true);
    }
}

async function deleteAdItem(adId) {
    const adminKey = getSavedAdminKey();
    if (adminKey === "") {
        showBanner("ابتدا کلید ادمین را وارد کنید.", true);
        return;
    }

    try {
        const res = await fetch("/ads/" + adId, {
            method: "DELETE",
            headers: {
                "X-Admin-Key": adminKey
            }
        });

        if (!res.ok) {
            const errData = await res.json();
            showBanner("خطا در حذف تبلیغ: " + (errData.detail || res.status), true);
            return;
        }

        showBanner("کمپین تبلیغاتی حذف شد.", false);
        loadAdminAds();
    } catch (err) {
        showBanner("خطا در ارتباط با سرور هنگام حذف تبلیغ.", true);
    }
}

async function loadAdminVideos() {
    const listBox = document.getElementById("adminVideoList");
    const adminKey = getSavedAdminKey();

    if (adminKey === "") {
        listBox.innerHTML = "<p class='muted-text'>برای دیدن لیست ویدیوها کلید ادمین را وارد کنید.</p>";
        return;
    }

    try {
        const res = await fetch("/videos/admin/all", {
            method: "GET",
            headers: {
                "X-Admin-Key": adminKey
            }
        });

        if (res.status === 401 || res.status === 403) {
            listBox.innerHTML = "<p class='muted-text'>کلید ادمین نامعتبر است.</p>";
            return;
        }

        if (!res.ok) {
            listBox.innerHTML = "<p class='muted-text'>خطا در دریافت لیست ویدیوها</p>";
            return;
        }

        const videos = await res.json();
        listBox.innerHTML = "";

        if (videos.length === 0) {
            listBox.innerHTML = "<p class='muted-text'>هیچ ویدیویی موجود نیست.</p>";
            return;
        }

        for (let i = 0; i < videos.length; i++) {
            const item = videos[i];

            const row = document.createElement("div");
            row.className = "list-row";

            const info = document.createElement("div");
            info.className = "row-info";

            const titleEl = document.createElement("div");
            titleEl.className = "row-title";
            titleEl.textContent = "#" + item.id + " - " + item.title;

            let statusText = "در حال پردازش HLS...";
            if (item.is_active === true) {
                statusText = "آماده پخش";
            }

            const metaEl = document.createElement("div");
            metaEl.className = "row-meta";
            metaEl.textContent = "وضعیت: " + statusText + " | بازدید: " + item.views_count + " | مدت: " + item.duration_seconds + " ثانیه";

            info.appendChild(titleEl);
            info.appendChild(metaEl);

            const delBtn = document.createElement("button");
            delBtn.type = "button";
            delBtn.className = "delete-btn";
            delBtn.textContent = "حذف";
            delBtn.addEventListener("click", function () {
                deleteVideoItem(item.id);
            });

            row.appendChild(info);
            row.appendChild(delBtn);
            listBox.appendChild(row);
        }
    } catch (err) {
        listBox.innerHTML = "<p class='muted-text'>عدم ارتباط با سرور</p>";
    }
}

async function loadAdminAds() {
    const listBox = document.getElementById("adminAdList");
    const adminKey = getSavedAdminKey();

    if (adminKey === "") {
        listBox.innerHTML = "<p class='muted-text'>برای دیدن لیست تبلیغات کلید ادمین را وارد کنید.</p>";
        return;
    }

    try {
        const res = await fetch("/ads/", {
            method: "GET",
            headers: {
                "X-Admin-Key": adminKey
            }
        });

        if (res.status === 401 || res.status === 403) {
            listBox.innerHTML = "<p class='muted-text'>کلید ادمین نامعتبر است.</p>";
            return;
        }

        if (!res.ok) {
            listBox.innerHTML = "<p class='muted-text'>خطا در دریافت لیست تبلیغات</p>";
            return;
        }

        const ads = await res.json();
        listBox.innerHTML = "";

        if (ads.length === 0) {
            listBox.innerHTML = "<p class='muted-text'>هیچ کمپین تبلیغاتی ثبت نشده است.</p>";
            return;
        }

        for (let i = 0; i < ads.length; i++) {
            const ad = ads[i];

            const row = document.createElement("div");
            row.className = "list-row";

            const info = document.createElement("div");
            info.className = "row-info";

            const titleEl = document.createElement("div");
            titleEl.className = "row-title";
            titleEl.textContent = "#" + ad.id + " - " + ad.campaign_name;

            const metaEl = document.createElement("div");
            metaEl.className = "row-meta";
            metaEl.textContent = "نمایش: " + ad.impressions_count + " | کلیک: " + ad.clicks_count + " | اسکیپ: " + ad.skip_after_seconds + " ثانیه";

            info.appendChild(titleEl);
            info.appendChild(metaEl);

            const delBtn = document.createElement("button");
            delBtn.type = "button";
            delBtn.className = "delete-btn";
            delBtn.textContent = "حذف";
            delBtn.addEventListener("click", function () {
                deleteAdItem(ad.id);
            });

            row.appendChild(info);
            row.appendChild(delBtn);
            listBox.appendChild(row);
        }
    } catch (err) {
        listBox.innerHTML = "<p class='muted-text'>عدم ارتباط با سرور</p>";
    }
}

async function handleVideoUpload(event) {
    event.preventDefault();

    const adminKey = getSavedAdminKey();
    if (adminKey === "") {
        showBanner("ابتدا کلید ادمین را وارد کرده و دکمه اتصال را بزنید.", true);
        return;
    }

    const fileInput = document.getElementById("vidFile");
    if (!fileInput.files || fileInput.files.length === 0) {
        showBanner("فایل ویدیو انتخاب نشده است.", true);
        return;
    }

    const formData = new FormData();
    formData.append("title", document.getElementById("vidTitle").value);
    formData.append("description", document.getElementById("vidDesc").value);
    formData.append("duration_seconds", document.getElementById("vidDuration").value);
    formData.append("video_file", fileInput.files[0]);

    showBanner("در حال آپلود فایل ویدیو...", false);

    try {
        const res = await fetch("/videos/upload", {
            method: "POST",
            headers: {
                "X-Admin-Key": adminKey
            },
            body: formData
        });

        if (!res.ok) {
            const errData = await res.json();
            showBanner("خطا در آپلود ویدیو: " + (errData.detail || res.status), true);
            return;
        }

        document.getElementById("videoUploadForm").reset();
        showBanner("فایل آپلود شد و در پس‌زمینه در حال تبدیل به HLS است. چند ثانیه بعد بروزرسانی را بزنید.", false);
        loadAdminVideos();
    } catch (err) {
        showBanner("خطا در اتصال به سرور هنگام آپلود ویدیو.", true);
    }
}

async function handleAdUpload(event) {
    event.preventDefault();

    const adminKey = getSavedAdminKey();
    if (adminKey === "") {
        showBanner("ابتدا کلید ادمین را وارد کرده و دکمه اتصال را بزنید.", true);
        return;
    }

    const fileInput = document.getElementById("adFile");
    if (!fileInput.files || fileInput.files.length === 0) {
        showBanner("فایل تبلیغ انتخاب نشده است.", true);
        return;
    }

    const formData = new FormData();
    formData.append("campaign_name", document.getElementById("adName").value);
    formData.append("target_click_url", document.getElementById("adClickUrl").value);
    formData.append("skip_after_seconds", document.getElementById("adSkipSec").value);
    formData.append("ad_file", fileInput.files[0]);

    showBanner("در حال آپلود تبلیغ...", false);

    try {
        const res = await fetch("/ads/upload", {
            method: "POST",
            headers: {
                "X-Admin-Key": adminKey
            },
            body: formData
        });

        if (!res.ok) {
            const errData = await res.json();
            showBanner("خطا در آپلود تبلیغ: " + (errData.detail || res.status), true);
            return;
        }

        document.getElementById("adUploadForm").reset();
        showBanner("کمپین تبلیغاتی با موفقیت ثبت شد.", false);
        loadAdminAds();
    } catch (err) {
        showBanner("خطا در اتصال به سرور هنگام آپلود تبلیغ.", true);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const savedKey = sessionStorage.getItem(STORAGE_KEY_NAME);
    if (savedKey !== null && savedKey.trim() !== "") {
        document.getElementById("adminKeyInput").value = savedKey;
        loadAdminVideos();
        loadAdminAds();
    } else {
        showLockedLists("ابتدا کلید ادمین را وارد کنید.");
    }

    document.getElementById("saveKeyBtn").addEventListener("click", verifyAndConnectAdmin);
    document.getElementById("videoUploadForm").addEventListener("submit", handleVideoUpload);
    document.getElementById("adUploadForm").addEventListener("submit", handleAdUpload);
    document.getElementById("refreshVideosBtn").addEventListener("click", loadAdminVideos);
    document.getElementById("refreshAdsBtn").addEventListener("click", loadAdminAds);
});