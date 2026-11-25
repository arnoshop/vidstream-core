let activePlayerInstance = null;

async function checkApiHealth() {
    const statusEl = document.getElementById("apiStatus");
    try {
        const res = await fetch("/health");
        if (res.ok) {
            statusEl.textContent = "سرور متصل است";
            statusEl.style.color = "#4ade80";
        } else {
            statusEl.textContent = "خطا در سرور";
            statusEl.style.color = "#f87171";
        }
    } catch (err) {
        statusEl.textContent = "قطع ارتباط با سرور";
        statusEl.style.color = "#f87171";
    }
}

function getSourceMimeType(urlText) {
    const lowerUrl = urlText.toLowerCase();
    if (lowerUrl.indexOf(".m3u8") !== -1) {
        return "application/x-mpegURL";
    }
    return "video/mp4";
}

function formatDuration(totalSeconds) {
    const num = parseInt(totalSeconds, 10);
    if (isNaN(num) || num <= 0) {
        return "00:00";
    }

    const mins = Math.floor(num / 60);
    const secs = num % 60;

    let minText = String(mins);
    if (mins < 10) {
        minText = "0" + minText;
    }

    let secText = String(secs);
    if (secs < 10) {
        secText = "0" + secText;
    }

    return minText + ":" + secText;
}

function setupVideoPlayer(streamUrl, thumbnailUrl) {
    if (activePlayerInstance !== null) {
        try {
            activePlayerInstance.destroy();
        } catch (err) {
            console.log("player destroy warning:", err);
        }
        activePlayerInstance = null;
    }

    const container = document.getElementById("playerContainer");
    container.innerHTML = "";

    const videoEl = document.createElement("video");
    videoEl.id = "mainVideoPlayer";
    videoEl.setAttribute("controls", "true");
    videoEl.setAttribute("playsinline", "true");

    let posterValue = false;
    if (thumbnailUrl && thumbnailUrl.trim() !== "") {
        posterValue = thumbnailUrl.trim();
        videoEl.setAttribute("poster", posterValue);
    }

    const sourceEl = document.createElement("source");
    sourceEl.src = streamUrl;
    sourceEl.type = getSourceMimeType(streamUrl);

    videoEl.appendChild(sourceEl);
    container.appendChild(videoEl);

    if (typeof fluidPlayer === "function") {
        activePlayerInstance = fluidPlayer("mainVideoPlayer", {
            layoutControls: {
                fillToContainer: true,
                autoPlay: false,
                mute: false,
                posterImage: posterValue
            },
            vastOptions: {
                adList: [
                    {
                        roll: "preRoll",
                        vastTag: "/ads/vast.xml"
                    }
                ]
            }
        });
    }
}

async function openVideoBySlug(slugValue) {
    try {
        const response = await fetch("/videos/" + encodeURIComponent(slugValue));
        if (!response.ok) {
            return;
        }

        const videoData = await response.json();

        document.getElementById("videoTitle").textContent = videoData.title;
        document.getElementById("videoViews").textContent = "بازدید: " + videoData.views_count;
        document.getElementById("videoDuration").textContent = "مدت: " + formatDuration(videoData.duration_seconds);

        if (videoData.description) {
            document.getElementById("videoDescription").textContent = videoData.description;
        } else {
            document.getElementById("videoDescription").textContent = "توضیحاتی ثبت نشده است.";
        }

        setupVideoPlayer(videoData.stream_url, videoData.thumbnail_url);
    } catch (err) {
        console.log("failed to load video:", err);
    }
}

async function loadVideoList() {
    const listContainer = document.getElementById("videoList");

    try {
        const response = await fetch("/videos/");
        if (!response.ok) {
            listContainer.innerHTML = "<p class='empty-msg'>خطا در دریافت لیست ویدیوها</p>";
            return;
        }

        const videos = await response.json();
        listContainer.innerHTML = "";

        if (videos.length === 0) {
            listContainer.innerHTML = "<p class='empty-msg'>هنوز هیچ ویدیویی ثبت نشده است.</p>";
            return;
        }

        for (let i = 0; i < videos.length; i++) {
            const item = videos[i];

            const card = document.createElement("div");
            card.className = "video-card";

            const thumbBox = document.createElement("div");
            thumbBox.className = "video-thumb-box";

            if (item.thumbnail_url && item.thumbnail_url.trim() !== "") {
                const imgEl = document.createElement("img");
                imgEl.className = "video-thumb-img";
                imgEl.src = item.thumbnail_url;
                imgEl.alt = item.title;
                thumbBox.appendChild(imgEl);
            } else {
                const placeholder = document.createElement("span");
                placeholder.className = "video-thumb-placeholder";
                placeholder.textContent = "بدون کاور";
                thumbBox.appendChild(placeholder);
            }

            const bodyDiv = document.createElement("div");
            bodyDiv.className = "video-card-body";

            const titleDiv = document.createElement("div");
            titleDiv.className = "video-card-title";
            titleDiv.textContent = item.title;

            const subDiv = document.createElement("div");
            subDiv.className = "video-card-sub";
            subDiv.textContent = "بازدید: " + item.views_count + " | مدت: " + formatDuration(item.duration_seconds);

            bodyDiv.appendChild(titleDiv);
            bodyDiv.appendChild(subDiv);

            card.appendChild(thumbBox);
            card.appendChild(bodyDiv);

            card.addEventListener("click", function () {
                openVideoBySlug(item.slug);
            });

            listContainer.appendChild(card);
        }

        openVideoBySlug(videos[0].slug);
    } catch (err) {
        listContainer.innerHTML = "<p class='empty-msg'>عدم دسترسی به API</p>";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    checkApiHealth();
    loadVideoList();
});