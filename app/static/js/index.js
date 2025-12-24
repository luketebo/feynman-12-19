// 现在可以直接使用 window.FLASK_CONFIG 中的数据了
const sessionId = window.FLASK_CONFIG.sessionId;
const avatarSrc = window.FLASK_CONFIG.avatarUrl;

const messageBox = document.getElementById("message-box");
messageBox.scrollTop = messageBox.scrollHeight;
//const sessionId = {{ chat_session.id }};

async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    // 添加用户消息到界面
    appendMessage("user", text);
    input.value = "";

    // 创建 AI 回复的占位容器
    const aiMessageDiv = appendMessage("assistant", "");
    aiMessageDiv.classList.add("typing");
    let fullReply = "";

    try {
        const response = await fetch(window.FLASK_CONFIG.chatStreamUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });
        /*
        const response = await fetch("{{ url_for('chat.chat_stream') }}", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: sessionId }),
        });
        */

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();

            if (value) {
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop();

                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (trimmedLine.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(trimmedLine.slice(6));
                            if (data.chunk) {
                                fullReply += data.chunk;
                                aiMessageDiv.textContent = fullReply;
                                messageBox.scrollTop = messageBox.scrollHeight;
                            }

                            if (data.done) {
                                updateStatus(data);
                            }
                        } catch (e) {
                            console.warn(
                                "Error parsing chunk:",
                                e,
                                trimmedLine
                            );
                        }
                    }
                }
            }

            if (done) break;
        }

        aiMessageDiv.classList.remove("typing");
    } catch (e) {
        console.error(e);
        aiMessageDiv.textContent = "哎呀，费曼的小脑袋出错了：" + e.message;
        aiMessageDiv.classList.remove("typing");
    }
}

function appendMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    messageBox.appendChild(div);
    messageBox.scrollTop = messageBox.scrollHeight;
    return div;
}

function updateStatus(status) {
    document.getElementById("pet-level").textContent = `Lv. ${status.level}`;
    document.getElementById("pet-exp").textContent = `${status.experience} / ${
        status.level * 100
    }`;
    document.getElementById("user-coins").textContent = `💰 ${status.coins}`;
    if (status.knowledge) {
        document.getElementById("pet-knowledge").textContent = status.knowledge;
        const count = status.knowledge
            .split("\n")
            .filter((line) => line.trim()).length;
        document.getElementById("knowledge-count").textContent = count;
    }
}
async function callPhone() {
    console.log("拨打电话...");

    const container = document.querySelector(".chat-container");
    if (!container) return;

    // 每次都重新创建蒙版，保证动画状态重置
    let overlay = document.getElementById("phone-call-overlay");
    if (overlay) overlay.remove(); // 如果已有，先移除，防止重复

    overlay = document.createElement("div");
    overlay.id = "phone-call-overlay";
    overlay.className = "call-overlay";

    //const avatar = "/static/img/doujun_normal.png";
    const avatar = window.FLASK_CONFIG.avatarUrl;
    // HTML 结构：分为 center-content (中间) 和 controls (底部)
    const contentHTML = `<div class="call-center-content">
            <!-- 加载圈，初始显示 -->
            <div class="loader" id="call-loader"></div>

            <!-- 大头像 (接通后显示，初始隐藏) -->
            <img
                id="call-avatar2"
                src="${avatar}"
                alt="头像"
                style="
                    display: none; /* 初始隐藏，保持原有逻辑 */
                    width: 100px; /* 宽度：控制大小 (原文字是80px，图片100px视觉上差不多) */
                    height: 100px; /* 高度：保持正方形 */
                    border-radius: 50%; /* 变成圆形 */
                    object-fit: cover; /* 防止图片变形 (裁剪填充) */
                    margin-bottom: 20px; /* 底部留白 */
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* 加一点阴影更立体 */
                    border: 3px solid white; /* 可选：加一个白边框 */
                "
            />

            <!-- 状态文字 -->
            <div class="thinking-text" id="call-status-text">
                正在呼叫费曼...
            </div>
            <!-- 【新增】提示文字区域 -->
            <!-- min-height 是为了占位，防止文字出现时页面抖动 -->
            <div
                id="call-hint-text"
                style="
                    min-height: 20px;
                    font-size: 0.9rem;
                    color: #ff3b30;
                    opacity: 0;
                    transition: opacity 0.5s;
                    margin-bottom: 20px;
                "
            ></div>
        </div>

        <!-- 底部按钮区，初始 CSS opacity 为 0 -->
        <div class="call-controls" id="call-controls-area">
            <!-- 1. 麦克风 -->
            <button class="control-btn" onclick="toggleMic(this)">
                <svg
                    t="1766577448984"
                    class="icon"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                    p-id="6729"
                    width="200"
                    height="200"
                >
                    <path
                        d="M511.752 70.5c-86.605 0-156.835 69.734-156.835 155.747l0 273.812c0 86.013 70.23 155.748 156.835 155.748 86.602 0 156.832-69.735 156.832-155.748L668.584 226.247C668.584 140.234 598.354 70.5 511.752 70.5L511.752 70.5 511.752 70.5zM243.854 461.102c-18.051 0-32.649 14.496-32.649 32.451 0 2.269 0.197 4.436 0.689 6.506l-0.689 0c0 151.605 113.922 276.578 261.386 295.713l0 80.687-52.275 0c-21.702 0-39.257 17.458-39.257 38.964 0 21.499 17.555 38.957 39.257 38.957l182.969 0c21.701 0 39.256-17.458 39.256-38.957 0-21.506-17.555-38.964-39.256-38.964L551.01 876.459l0-80.687c143.119-18.543 254.383-137.002 260.691-282.688 0.396-2.072 0.695-4.243 0.695-6.512 0-0.79-0.197-1.479-0.197-2.167 0-1.483 0.197-2.86 0.197-4.345l-0.695 0c-3.058-14.795-16.172-25.94-32.057-25.94-15.782 0-28.999 11.145-32.057 25.94l-0.688 0c0 129.019-105.344 233.572-235.249 233.572-129.903 0-235.249-104.554-235.249-233.572l-0.689 0c0.396-2.07 0.689-4.237 0.689-6.506C276.503 475.598 261.906 461.102 243.854 461.102L243.854 461.102 243.854 461.102zM243.854 461.102"
                        fill="#272636"
                        p-id="6730"
                    ></path>
                </svg>
            </button>

            <!-- 2. 挂断 (红色) -->
            <button class="control-btn btn-hangup" id="btn-hangup">
                <svg
                    t="1766577423821"
                    class="icon"
                    viewBox="0 0 1051 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                    p-id="5668"
                    width="200"
                    height="200"
                >
                    <path
                        d="M0 512a525.653333 512 0 1 0 1051.306667 0 525.653333 512 0 1 0-1051.306667 0Z"
                        fill="#CC333B"
                        p-id="5669"
                    ></path>
                    <path
                        d="M394.581333 527.018667c0 1.365333-1.365333 16.384-1.365333 20.48 0 8.192-1.365333 13.653333-2.730667 20.48-8.192 42.325333-38.229333 64.170667-107.861333 70.997333-43.690667 4.096-72.362667-5.461333-87.381333-30.037333-10.922667-17.749333-13.653333-38.229333-10.922667-70.997334 0-2.730667 1.365333-20.48 1.365333-25.941333 4.096-76.458667 165.205333-147.456 354.986667-146.090667 191.146667 1.365333 345.429333 73.728 341.333333 151.552v21.845334c-1.365333 39.594667-6.826667 62.805333-24.576 80.554666-17.749333 17.749333-45.056 25.941333-84.650666 20.48-80.554667-9.557333-105.130667-35.498667-102.4-94.208 0-4.096 1.365333-19.114667 1.365333-20.48 1.365333-13.653333-51.882667-25.941333-136.533333-25.941333-86.016 1.365333-140.629333 12.288-140.629334 27.306667z"
                        fill="#FFFFFF"
                        p-id="5670"
                    ></path>
                </svg>
            </button>

            <!-- 3. 更多 -->
            <button class="control-btn" onclick="alert('更多功能...')">
                <svg
                    t="1766577217031"
                    class="icon"
                    viewBox="0 0 1024 1024"
                    version="1.1"
                    xmlns="http://www.w3.org/2000/svg"
                    p-id="4704"
                    width="200"
                    height="200"
                >
                    <path
                        d="M506.197333 31.744C240.981333 31.744 25.941333 246.784 25.941333 512s215.04 480.256 480.256 480.256S986.453333 777.216 986.453333 512 771.413333 31.744 506.197333 31.744z m-217.770666 539.306667H286.72c-32.768 0-59.050667-26.282667-59.050667-59.050667s26.282667-59.050667 59.050667-59.050667h1.706667c32.768 0 59.050667 26.282667 59.050666 59.050667s-26.282667 59.050667-59.050666 59.050667z m218.794666 0h-1.706666c-32.768 0-59.050667-26.282667-59.050667-59.050667s26.282667-59.050667 59.050667-59.050667h1.706666c32.768 0 59.050667 26.282667 59.050667 59.050667s-26.282667 59.050667-59.050667 59.050667z m218.453334 0h-1.706667c-32.768 0-59.050667-26.282667-59.050667-59.050667s26.282667-59.050667 59.050667-59.050667h1.706667c32.768 0 59.050667 26.282667 59.050666 59.050667s-26.282667 59.050667-59.050666 59.050667z"
                        p-id="4705"
                    ></path>
                </svg>
            </button>
        </div> `;

    overlay.innerHTML = contentHTML;
    container.appendChild(overlay);

    // --- 计时器逻辑变量 ---
    let timerInterval = null; // 用于存储定时器ID
    let seconds = 0; // 记录通话秒数

    // 2. 设置延时，模拟接通
    setTimeout(() => {
        // 如果用户在2秒内已经挂断了，就不要执行后面的逻辑
        //if (!document.getElementById("phone-call-overlay")) return;

        // UI 切换：隐藏转圈，显示头像和按钮
        //document.getElementById("call-loader").style.display = "none";
        //document.getElementById("call-avatar").style.display = "block";

        console.log(">>> 2秒定时器开始执行");

        // 1. 检查父容器
        const overlay = document.getElementById("phone-call-overlay");
        if (!overlay) {
            console.warn("未找到 id='phone-call-overlay'，逻辑中止。");
            return;
        }

        // 2. 检查 loader 元素
        const loader = document.getElementById("call-loader");
        if (!loader) {
            console.error(
                "未找到 id='call-loader'。原因：contentHTML 可能未插入 DOM 或 ID 拼写错误。"
            );
            return;
        }

        // 3. 检查 avatar 元素
        const avatarImg = document.getElementById("call-avatar2");
        if (!avatarImg) {
            console.error("未找到 id='call-avatar'。");
            return;
        }

        // --- 执行逻辑 ---
        console.log("元素检查通过，开始切换 UI...");

        loader.style.display = "none";
        avatarImg.style.display = "block"; // 关键点

        console.log("头像 display 属性已设置为:", avatarImg.style.display);

        document.getElementById("call-controls-area").classList.add("visible");

        const statusText = document.getElementById("call-status-text");

        // --- 【新增】接通时的提示逻辑 ---
        const hintText = document.getElementById("call-hint-text");
        if (hintText) {
            hintText.innerText = "您可以开始说话了";
            hintText.style.color = "#666"; // 正常提示用灰色
            hintText.style.opacity = "1"; // 显示

            // 3秒后自动消失
            setTimeout(() => {
                // 只有当前不是“静音”状态时，才隐藏文字
                const micBtn = document.getElementById("btn-mic");
                if (micBtn && !micBtn.classList.contains("muted")) {
                    hintText.style.opacity = "0";
                }
            }, 3000);
        } // <--- 【修复点】这里补上了 if (hintText) 的结束大括号

        // --- 开始计时 (放在 if 外面更安全) ---
        statusText.innerText = "00:00"; // 初始时间

        timerInterval = setInterval(() => {
            seconds++;
            // 格式化时间：将秒数转换成 MM:SS 格式
            const mins = Math.floor(seconds / 60)
                .toString()
                .padStart(2, "0");
            const secs = (seconds % 60).toString().padStart(2, "0");
            statusText.innerText = `${mins}:${secs}`;
        }, 1000); // 每1000毫秒(1秒)执行一次
    }, 2000); // 等待2秒

    // 3. 挂断事件处理
    const hangupBtn = document.getElementById("btn-hangup");
    hangupBtn.onclick = function (e) {
        e.stopPropagation();

        // 关键步骤：清除定时器！停止计时
        if (timerInterval) {
            clearInterval(timerInterval);
        }

        overlay.remove();
        console.log(`通话结束，时长: ${seconds}秒`);
    };

    const MIC_ON_SVG =
        '<svg t="1766577448984" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="6729" width="200" height="200"><path d="M511.752 70.5c-86.605 0-156.835 69.734-156.835 155.747l0 273.812c0 86.013 70.23 155.748 156.835 155.748 86.602 0 156.832-69.735 156.832-155.748L668.584 226.247C668.584 140.234 598.354 70.5 511.752 70.5L511.752 70.5 511.752 70.5zM243.854 461.102c-18.051 0-32.649 14.496-32.649 32.451 0 2.269 0.197 4.436 0.689 6.506l-0.689 0c0 151.605 113.922 276.578 261.386 295.713l0 80.687-52.275 0c-21.702 0-39.257 17.458-39.257 38.964 0 21.499 17.555 38.957 39.257 38.957l182.969 0c21.701 0 39.256-17.458 39.256-38.957 0-21.506-17.555-38.964-39.256-38.964L551.01 876.459l0-80.687c143.119-18.543 254.383-137.002 260.691-282.688 0.396-2.072 0.695-4.243 0.695-6.512 0-0.79-0.197-1.479-0.197-2.167 0-1.483 0.197-2.86 0.197-4.345l-0.695 0c-3.058-14.795-16.172-25.94-32.057-25.94-15.782 0-28.999 11.145-32.057 25.94l-0.688 0c0 129.019-105.344 233.572-235.249 233.572-129.903 0-235.249-104.554-235.249-233.572l-0.689 0c0.396-2.07 0.689-4.237 0.689-6.506C276.503 475.598 261.906 461.102 243.854 461.102L243.854 461.102 243.854 461.102zM243.854 461.102" fill="#272636" p-id="6730"></path></svg>';

    const MIC_OFF_SVG =
        '<svg t="1766577896826" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="9737" width="200" height="200"><path d="M523.52 154.453333A142.506667 142.506667 0 0 0 381.866667 298.666667v238.933333l278.613333-278.613333a142.506667 142.506667 0 0 0-136.96-104.533334zM329.813333 589.653333a201.813333 201.813333 0 0 1-8.96-59.733333v-42.666667a30.293333 30.293333 0 0 0-61.013333 0v42.666667a261.973333 261.973333 0 0 0 22.613333 106.666667zM523.52 682.666667a142.506667 142.506667 0 0 0 142.08-142.08V420.693333l128-128a30.72 30.72 0 0 0 0-42.666666 30.293333 30.293333 0 0 0-35.84-4.693334 29.44 29.44 0 0 1-4.693333 7.253334L276.48 729.173333a29.44 29.44 0 0 1-7.253333 4.693334 30.293333 30.293333 0 0 0 4.693333 35.84 30.72 30.72 0 0 0 42.666667 0l37.973333-37.973334a262.826667 262.826667 0 0 0 138.666667 60.16v72.96H371.626667a30.293333 30.293333 0 0 0 0 61.013334h304.213333a30.293333 30.293333 0 0 0 0-61.013334H554.666667v-72.96a264.106667 264.106667 0 0 0 233.386666-261.973333v-42.666667a30.293333 30.293333 0 1 0-61.013333 0v42.666667a202.666667 202.666667 0 0 1-328.96 158.72l37.546667-37.546667a141.226667 141.226667 0 0 0 87.893333 31.573334z" fill="#ED404C" p-id="9738"></path></svg>';

    // 麦克风切换功能
    window.toggleMic = function (btn) {
        btn.classList.toggle("muted");
        const isMuted = btn.classList.contains("muted");

        // 获取提示元素
        const hintText = document.getElementById("call-hint-text");

        if (isMuted) {
            // --- 静音状态 ---
            btn.innerHTML = MIC_OFF_SVG;
            btn.style.backgroundColor = "#fff";

            // 【新增】显示静音提示
            if (hintText) {
                hintText.innerText = "您已静音";
                hintText.style.color = "#ff3b30"; // 红色，警示效果
                hintText.style.opacity = "1"; // 常驻显示
            }
        } else {
            // --- 恢复正常 ---
            btn.innerHTML = MIC_ON_SVG;
            btn.style.backgroundColor = "#e0e0e0";

            // 【新增】隐藏提示
            if (hintText) {
                hintText.style.opacity = "0"; // 渐隐消失
            }
        }
    };
}
