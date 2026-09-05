/* ============================================================
   SUPPLYSHIELD AI
   FRONTEND APPLICATION
   ============================================================ */


/* ============================================================
   GLOBAL STATE
   ============================================================ */

let currentCase = null;
let currentImpact = null;
let currentActionPlan = null;

let currentUser = null;


/* ============================================================
   AUTHENTICATION
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    checkAuthentication();

    setupNavigation();

    setupCharacterCounter();

});


/* ------------------------------------------------------------
   CHECK LOGIN
   ------------------------------------------------------------ */

function checkAuthentication() {

    const savedUser = localStorage.getItem("supplyshield_user");

    const authScreen = document.getElementById("auth-screen");
    const mainApp = document.getElementById("main-app");

    if (savedUser) {

        try {

            currentUser = JSON.parse(savedUser);

            showMainApplication();

        } catch (error) {

            localStorage.removeItem("supplyshield_user");

            showAuthentication();

        }

    } else {

        showAuthentication();

    }

}


/* ------------------------------------------------------------
   SHOW AUTHENTICATION
   ------------------------------------------------------------ */

function showAuthentication() {

    const authScreen = document.getElementById("auth-screen");
    const mainApp = document.getElementById("main-app");

    if (authScreen) {
        authScreen.style.display = "flex";
    }

    if (mainApp) {
        mainApp.style.display = "none";
    }

}


/* ------------------------------------------------------------
   SHOW MAIN APPLICATION
   ------------------------------------------------------------ */

function showMainApplication() {

    const authScreen = document.getElementById("auth-screen");
    const mainApp = document.getElementById("main-app");

    if (authScreen) {
        authScreen.style.display = "none";
    }

    if (mainApp) {
        mainApp.style.display = "flex";
    }

    loadUserProfile();

    loadDashboard();

    loadHistory();

}


/* ------------------------------------------------------------
   SHOW LOGIN
   ------------------------------------------------------------ */

function showLogin() {

    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");

    loginForm.classList.remove("hidden-auth");
    signupForm.classList.add("hidden-auth");

    clearAuthMessage("login-message");
    clearAuthMessage("signup-message");

}


/* ------------------------------------------------------------
   SHOW SIGNUP
   ------------------------------------------------------------ */

function showSignup() {

    const loginForm = document.getElementById("login-form");
    const signupForm = document.getElementById("signup-form");

    loginForm.classList.add("hidden-auth");
    signupForm.classList.remove("hidden-auth");

    clearAuthMessage("login-message");
    clearAuthMessage("signup-message");

}


/* ------------------------------------------------------------
   LOGIN
   ------------------------------------------------------------ */

async function handleLogin() {

    const email = document
        .getElementById("login-email")
        .value
        .trim();

    const password = document
        .getElementById("login-password")
        .value;

    if (!email || !password) {

        showAuthMessage(
            "login-message",
            "Please enter your email and password.",
            "error"
        );

        return;

    }


    try {

        const response = await fetch("/api/auth/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })

        });


        const data = await response.json();


        if (!response.ok) {

            showAuthMessage(
                "login-message",
                data.detail || "Login failed.",
                "error"
            );

            return;

        }


        if (!data.success) {

            showAuthMessage(
                "login-message",
                data.message || "Invalid email or password.",
                "error"
            );

            return;

        }


        currentUser = data.user;

        localStorage.setItem(
            "supplyshield_user",
            JSON.stringify(currentUser)
        );


        showAuthMessage(
            "login-message",
            "Login successful. Opening control tower...",
            "success"
        );


        setTimeout(() => {

            showMainApplication();

        }, 500);


    } catch (error) {

        console.error("Login error:", error);

        showAuthMessage(
            "login-message",
            "Unable to connect to SupplyShield server.",
            "error"
        );

    }

}


/* ------------------------------------------------------------
   SIGNUP
   ------------------------------------------------------------ */

async function handleSignup() {

    const name = document
        .getElementById("signup-name")
        .value
        .trim();

    const email = document
        .getElementById("signup-email")
        .value
        .trim();

    const password = document
        .getElementById("signup-password")
        .value;

    const confirmPassword = document
        .getElementById("signup-confirm")
        .value;


    if (!name || !email || !password || !confirmPassword) {

        showAuthMessage(
            "signup-message",
            "Please complete all fields.",
            "error"
        );

        return;

    }


    if (password.length < 6) {

        showAuthMessage(
            "signup-message",
            "Password must contain at least 6 characters.",
            "error"
        );

        return;

    }


    if (password !== confirmPassword) {

        showAuthMessage(
            "signup-message",
            "Passwords do not match.",
            "error"
        );

        return;

    }


    try {

        const response = await fetch("/api/auth/signup", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })

        });


        const data = await response.json();


        if (!response.ok) {

            showAuthMessage(
                "signup-message",
                data.detail || "Unable to create account.",
                "error"
            );

            return;

        }


        if (!data.success) {

            showAuthMessage(
                "signup-message",
                data.message || "Unable to create account.",
                "error"
            );

            return;

        }


        showAuthMessage(
            "signup-message",
            "Account created successfully. You can now sign in.",
            "success"
        );


        document.getElementById("signup-password").value = "";
        document.getElementById("signup-confirm").value = "";


        setTimeout(() => {

            document.getElementById("login-email").value = email;

            showLogin();

            showAuthMessage(
                "login-message",
                "Account created. Please sign in.",
                "success"
            );

        }, 900);


    } catch (error) {

        console.error("Signup error:", error);

        showAuthMessage(
            "signup-message",
            "Unable to connect to SupplyShield server.",
            "error"
        );

    }

}


/* ------------------------------------------------------------
   LOGOUT
   ------------------------------------------------------------ */

function logout() {

    const confirmed = confirm(
        "Are you sure you want to logout?"
    );

    if (!confirmed) {
        return;
    }


    localStorage.removeItem("supplyshield_user");

    currentUser = null;
    currentCase = null;
    currentImpact = null;
    currentActionPlan = null;


    showAuthentication();


    document.getElementById("login-email").value = "";
    document.getElementById("login-password").value = "";

    showLogin();


    showToast("Logged out successfully.");

}


/* ------------------------------------------------------------
   LOAD USER PROFILE
   ------------------------------------------------------------ */

function loadUserProfile() {

    if (!currentUser) {
        return;
    }


    const nameElement =
        document.getElementById("user-name");

    const roleElement =
        document.getElementById("user-role");

    const avatarElement =
        document.getElementById("user-avatar");


    if (nameElement) {
        nameElement.textContent =
            currentUser.name || "User";
    }


    if (roleElement) {
        roleElement.textContent =
            currentUser.role || "Supply Chain Analyst";
    }


    if (avatarElement) {

        const name =
            currentUser.name || "User";

        avatarElement.textContent =
            name.charAt(0).toUpperCase();

    }

}


/* ------------------------------------------------------------
   AUTH MESSAGE
   ------------------------------------------------------------ */

function showAuthMessage(id, message, type) {

    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent = message;

    element.className =
        "auth-message show " + type;

}


function clearAuthMessage(id) {

    const element = document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent = "";

    element.className =
        "auth-message";

}


/* ============================================================
   NAVIGATION
   ============================================================ */

function setupNavigation() {

    const navItems =
        document.querySelectorAll(".nav-item");


    navItems.forEach(item => {

        item.addEventListener("click", () => {

            const page =
                item.dataset.page;

            showPage(page);

        });

    });

}


/* ------------------------------------------------------------
   SHOW PAGE
   ------------------------------------------------------------ */

function showPage(pageName) {

    if (!currentUser) {

        showAuthentication();

        return;

    }


    const pages =
        document.querySelectorAll(".page");

    pages.forEach(page => {

        page.classList.remove("active-page");

    });


    const targetPage =
        document.getElementById(
            pageName + "-page"
        );


    if (targetPage) {
        targetPage.classList.add("active-page");
    }


    const navItems =
        document.querySelectorAll(".nav-item");


    navItems.forEach(item => {

        item.classList.remove("active");

        if (item.dataset.page === pageName) {
            item.classList.add("active");
        }

    });


    updatePageTitle(pageName);


    if (pageName === "overview") {
        loadDashboard();
    }

    if (pageName === "history") {
        loadHistory();
    }

}


/* ------------------------------------------------------------
   PAGE TITLES
   ------------------------------------------------------------ */

function updatePageTitle(pageName) {

    const title =
        document.getElementById("page-title");


    const titles = {

        overview: "Supply Chain Overview",

        disruption: "New Disruption",

        impact: "Impact Analysis",

        actions: "Action Planner",

        orders: "Orders at Risk",

        evidence: "Evidence",

        history: "Disruption History"

    };


    if (title) {

        title.textContent =
            titles[pageName] || "SupplyShield AI";

    }

}


/* ============================================================
   CHARACTER COUNTER
   ============================================================ */

function setupCharacterCounter() {

    const textarea =
        document.getElementById(
            "disruption-notice"
        );

    const counter =
        document.getElementById(
            "character-count"
        );


    if (!textarea || !counter) {
        return;
    }


    textarea.addEventListener(
        "input",
        () => {

            counter.textContent =
                textarea.value.length +
                " characters";

        }
    );

}


/* ============================================================
   DEMO NOTICE
   ============================================================ */

function loadDemoNotice() {

    const textarea =
        document.getElementById(
            "disruption-notice"
        );


    if (!textarea) {
        return;
    }


    textarea.value =
        "Nova Components Ltd has announced an unexpected production halt due to machinery failure. Production will stop for 7 days. Motor Controller shipments may be delayed.";


    textarea.dispatchEvent(
        new Event("input")
    );


    showToast(
        "Demo disruption notice loaded."
    );

}


/* ============================================================
   DISRUPTION ANALYSIS
   ============================================================ */

async function analyzeDisruption() {

    const textarea =
        document.getElementById(
            "disruption-notice"
        );

    const button =
        document.getElementById(
            "analyze-button"
        );

    const result =
        document.getElementById(
            "analysis-result"
        );


    if (!textarea || !button) {
        return;
    }


    const notice =
        textarea.value.trim();


    if (!notice) {

        showToast(
            "Please enter a disruption notice."
        );

        return;

    }


    button.disabled = true;

    button.innerHTML =
        "<span>Analyzing...</span><span>⟳</span>";


    if (result) {

        result.classList.remove("hidden");

        result.innerHTML = `
            <div class="panel">
                <h3>Analyzing disruption...</h3>
                <p>
                    Extracting facts and tracing supply-chain impact.
                </p>
            </div>
        `;

    }


    try {

        const response =
            await fetch(
                "/api/disruption/analyze",
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        notice: notice
                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Analysis failed."
            );

        }


        currentCase =
            data.case || data;

        currentImpact =
            data.impact || null;

        currentActionPlan =
            data.action_plan || null;


        renderAnalysisResult(data);

        renderImpact(data.impact);

        renderActions(data.action_plan);

        renderOrders(data.impact);

        renderEvidence(data);


        showToast(
            "Disruption analysis completed."
        );


        loadDashboard();


        setTimeout(() => {

            showPage("impact");

        }, 800);


    } catch (error) {

        console.error(
            "Analysis error:",
            error
        );


        if (result) {

            result.innerHTML = `
                <div class="panel">
                    <h3>Analysis Failed</h3>
                    <p>
                        ${escapeHtml(error.message)}
                    </p>
                </div>
            `;

        }


        showToast(
            "Disruption analysis failed."
        );

    } finally {

        button.disabled = false;

        button.innerHTML =
            "<span>Analyze Disruption</span><span>→</span>";

    }

}


/* ============================================================
   ANALYSIS RESULT
   ============================================================ */

function renderAnalysisResult(data) {

    const container =
        document.getElementById(
            "analysis-result"
        );


    if (!container) {
        return;
    }


    const extracted =
        data.extracted || {};

    const impact =
        data.impact || {};


    const severity =
        impact.severity ||
        "UNKNOWN";


    const status =
        impact.status ||
        data.status ||
        "ANALYZED";


    container.classList.remove("hidden");


    container.innerHTML = `

        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        ANALYSIS COMPLETE
                    </span>

                    <h3>
                        Disruption Assessment
                    </h3>

                </div>

                <span class="severity-badge ${getSeverityClass(severity)}">
                    ${escapeHtml(severity)}
                </span>

            </div>


            <div class="stats-grid">

                <div class="stat-card">

                    <div class="stat-header">
                        STATUS
                    </div>

                    <div class="stat-value">
                        ${escapeHtml(status)}
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-header">
                        DISRUPTION TYPE
                    </div>

                    <div class="stat-value">
                        ${escapeHtml(
                            extracted.disruption_type ||
                            "Unknown"
                        )}
                    </div>

                </div>


                <div class="stat-card">

                    <div class="stat-header">
                        EXTRACTION
                    </div>

                    <div class="stat-value">
                        ${escapeHtml(
                            extracted.extraction_source ||
                            "AI"
                        )}
                    </div>

                </div>

            </div>


            <div style="margin-top:20px">

                <strong>
                    Reason
                </strong>

                <p>
                    ${escapeHtml(
                        impact.reason ||
                        "Impact analysis completed."
                    )}
                </p>

            </div>

        </div>
    `;

}


/* ============================================================
   IMPACT
   ============================================================ */

function renderImpact(impact) {

    const container =
        document.getElementById(
            "impact-content"
        );


    if (!container) {
        return;
    }


    if (!impact) {

        container.innerHTML = `
            <div class="empty-large">
                <div>◉</div>
                <h3>No disruption selected</h3>
                <p>Analyze a disruption first.</p>
            </div>
        `;

        return;

    }


    if (
        impact.status === "NO IMPACT"
        ||
        impact.severity === "NO IMPACT"
    ) {

        container.innerHTML = `

            <div class="panel">

                <div class="panel-heading">

                    <div>
                        <span class="panel-label">
                            IMPACT ASSESSMENT
                        </span>

                        <h3>
                            No Supply-Chain Impact Detected
                        </h3>
                    </div>

                    <span class="severity-badge">
                        NO IMPACT
                    </span>

                </div>

                <p>
                    ${escapeHtml(
                        impact.reason ||
                        "The disruption does not currently affect tracked supply-chain records."
                    )}
                </p>

            </div>
        `;

        return;

    }


    if (impact.status === "HUMAN REVIEW") {

        container.innerHTML = `

            <div class="panel">

                <div class="panel-heading">

                    <div>
                        <span class="panel-label">
                            REVIEW REQUIRED
                        </span>

                        <h3>
                            Human Review Required
                        </h3>
                    </div>

                    <span class="severity-badge critical">
                        REVIEW
                    </span>

                </div>

                <p>
                    ${escapeHtml(
                        impact.reason ||
                        "The disruption could not be mapped with sufficient confidence."
                    )}
                </p>

            </div>
        `;

        return;

    }


    const shipments =
        impact.affected_shipments ||
        [];

    const orders =
        impact.affected_orders ||
        [];

    const inventory =
        impact.affected_inventory ||
        [];


    container.innerHTML = `

        <div class="stats-grid">

            <div class="stat-card">

                <div class="stat-header">
                    AFFECTED SHIPMENTS
                </div>

                <div class="stat-value">
                    ${shipments.length}
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-header">
                    ORDERS AT RISK
                </div>

                <div class="stat-value">
                    ${orders.length}
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-header">
                    INVENTORY RECORDS
                </div>

                <div class="stat-value">
                    ${inventory.length}
                </div>

            </div>


            <div class="stat-card">

                <div class="stat-header">
                    SHORTAGE
                </div>

                <div class="stat-value">
                    ${impact.total_shortage || 0}
                </div>

            </div>

        </div>


        <div class="panel">

            <div class="panel-heading">

                <div>
                    <span class="panel-label">
                        IMPACT SUMMARY
                    </span>

                    <h3>
                        ${escapeHtml(
                            impact.severity ||
                            "Impact"
                        )}
                    </h3>
                </div>

                <span class="severity-badge ${getSeverityClass(
                    impact.severity
                )}">
                    ${escapeHtml(
                        impact.severity ||
                        "UNKNOWN"
                    )}
                </span>

            </div>

            <p>
                ${escapeHtml(
                    impact.reason ||
                    "Impact identified."
                )}
            </p>

        </div>


        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        AFFECTED SHIPMENTS
                    </span>

                    <h3>
                        Shipment Trace
                    </h3>

                </div>

            </div>

            ${renderShipmentTable(shipments)}

        </div>


        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        AFFECTED ORDERS
                    </span>

                    <h3>
                        Customer Impact
                    </h3>

                </div>

            </div>

            ${renderOrderTable(orders)}

        </div>
    `;

}


/* ============================================================
   SHIPMENT TABLE
   ============================================================ */

function renderShipmentTable(shipments) {

    if (!shipments.length) {

        return `
            <p class="empty-state">
                No affected shipments.
            </p>
        `;

    }


    return `

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>
                        <th>SHIPMENT</th>
                        <th>PRODUCT</th>
                        <th>QUANTITY</th>
                        <th>STATUS</th>
                        <th>EXPECTED</th>
                    </tr>

                </thead>

                <tbody>

                    ${shipments.map(shipment => `

                        <tr>

                            <td>
                                ${escapeHtml(
                                    shipment.shipment_id ||
                                    shipment.id ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    shipment.product_id ||
                                    shipment.product_name ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${shipment.quantity || 0}
                            </td>

                            <td>
                                ${escapeHtml(
                                    shipment.status ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    shipment.expected_date ||
                                    "-"
                                )}
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        </div>
    `;

}


/* ============================================================
   ORDER TABLE
   ============================================================ */

function renderOrderTable(orders) {

    if (!orders.length) {

        return `
            <p class="empty-state">
                No affected orders.
            </p>
        `;

    }


    return `

        <div class="table-wrapper">

            <table>

                <thead>

                    <tr>
                        <th>ORDER</th>
                        <th>CUSTOMER</th>
                        <th>PRODUCT</th>
                        <th>QTY</th>
                        <th>PRIORITY</th>
                        <th>DEADLINE</th>
                    </tr>

                </thead>

                <tbody>

                    ${orders.map(order => `

                        <tr>

                            <td>
                                ${escapeHtml(
                                    order.order_id ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    order.customer ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    order.product_id ||
                                    order.product_name ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${order.quantity || 0}
                            </td>

                            <td>
                                ${escapeHtml(
                                    order.priority ||
                                    "-"
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    order.deadline ||
                                    "-"
                                )}
                            </td>

                        </tr>

                    `).join("")}

                </tbody>

            </table>

        </div>
    `;

}


/* ============================================================
   ACTION PLAN
   ============================================================ */

function renderActions(plan) {

    const container =
        document.getElementById(
            "actions-content"
        );


    if (!container) {
        return;
    }


    if (!plan) {

        container.innerHTML = `
            <div class="empty-large">
                <div>➤</div>
                <h3>No action plan available</h3>
                <p>Analyze a disruption first.</p>
            </div>
        `;

        return;

    }


    if (plan.status === "NO IMPACT") {

        container.innerHTML = `
            <div class="panel">

                <span class="panel-label">
                    DECISION
                </span>

                <h3>
                    No Action Required
                </h3>

                <p>
                    No measurable supply-chain impact was identified.
                </p>

            </div>
        `;

        return;

    }


    if (plan.status === "HUMAN REVIEW") {

        container.innerHTML = `
            <div class="panel">

                <span class="panel-label">
                    DECISION SUPPORT
                </span>

                <h3>
                    Human Approval Required
                </h3>

                <p>
                    ${escapeHtml(
                        plan.reason ||
                        "The system cannot safely recommend an automated response."
                    )}
                </p>

            </div>
        `;

        return;

    }


    const options =
        plan.options || [];


    container.innerHTML = `

        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        RECOMMENDED RESPONSE
                    </span>

                    <h3>
                        ${escapeHtml(
                            plan.recommendation ||
                            "Review Options"
                        )}
                    </h3>

                </div>

                <span class="severity-badge critical">
                    HUMAN APPROVAL
                </span>

            </div>

            <p>
                The recommended action is decision support only.
                A human decision-maker should approve execution.
            </p>

        </div>


        <div class="dashboard-grid">

            ${options.map(option => `

                <div class="panel">

                    <div class="panel-heading">

                        <h3>
                            ${escapeHtml(
                                option.name ||
                                option.action ||
                                "Response Option"
                            )}
                        </h3>

                        ${
                            option.recommended
                            ?
                            `
                            <span class="severity-badge critical">
                                RECOMMENDED
                            </span>
                            `
                            :
                            ""
                        }

                    </div>


                    <p>
                        ${escapeHtml(
                            option.description ||
                            ""
                        )}
                    </p>


                    ${
                        option.pros
                        ?
                        `
                        <div style="margin-top:12px">

                            <strong>
                                Advantages
                            </strong>

                            <p>
                                ${escapeHtml(
                                    Array.isArray(option.pros)
                                    ? option.pros.join(", ")
                                    : option.pros
                                )}
                            </p>

                        </div>
                        `
                        :
                        ""
                    }


                    ${
                        option.cons
                        ?
                        `
                        <div style="margin-top:12px">

                            <strong>
                                Risks
                            </strong>

                            <p>
                                ${escapeHtml(
                                    Array.isArray(option.cons)
                                    ? option.cons.join(", ")
                                    : option.cons
                                )}
                            </p>

                        </div>
                        `
                        :
                        ""
                    }


                    ${
                        option.tradeoff
                        ?
                        `
                        <div style="margin-top:12px">

                            <strong>
                                Trade-off
                            </strong>

                            <p>
                                ${escapeHtml(
                                    option.tradeoff
                                )}
                            </p>

                        </div>
                        `
                        :
                        ""
                    }

                </div>

            `).join("")}

        </div>
    `;

}


/* ============================================================
   ORDERS PAGE
   ============================================================ */

function renderOrders(impact) {

    const container =
        document.getElementById(
            "orders-content"
        );


    if (!container) {
        return;
    }


    if (!impact || !impact.affected_orders) {

        return;

    }


    const orders =
        impact.affected_orders;


    if (!orders.length) {

        container.innerHTML = `

            <div class="empty-large">

                <div>▣</div>

                <h3>
                    No affected orders
                </h3>

                <p>
                    No customer orders are currently at risk.
                </p>

            </div>
        `;

        return;

    }


    container.innerHTML = `

        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        PRIORITY ORDERS
                    </span>

                    <h3>
                        Orders at Risk
                    </h3>

                </div>

                <span class="severity-badge critical">
                    ${orders.length} AT RISK
                </span>

            </div>


            ${renderOrderTable(orders)}

        </div>
    `;

}


/* ============================================================
   EVIDENCE
   ============================================================ */

function renderEvidence(data) {

    const container =
        document.getElementById(
            "evidence-content"
        );


    if (!container) {
        return;
    }


    const impact =
        data.impact || {};

    const evidence =
        impact.evidence ||
        data.traceability ||
        data.evidence ||
        [];


    if (!Array.isArray(evidence) || !evidence.length) {

        container.innerHTML = `

            <div class="panel">

                <span class="panel-label">
                    TRACEABILITY
                </span>

                <h3>
                    Evidence Records
                </h3>

                <p>
                    ${
                        escapeHtml(
                            impact.reason ||
                            "No evidence records returned."
                        )
                    }
                </p>

            </div>
        `;

        return;

    }


    container.innerHTML = `

        <div class="panel">

            <div class="panel-heading">

                <div>

                    <span class="panel-label">
                        DATA EVIDENCE
                    </span>

                    <h3>
                        Traceable Impact Claims
                    </h3>

                </div>

            </div>


            ${evidence.map((item, index) => `

                <div
                    style="
                        padding:15px;
                        border-bottom:1px solid rgba(255,255,255,0.06);
                    "
                >

                    <strong>
                        Evidence ${index + 1}
                    </strong>

                    <p>
                        ${escapeHtml(
                            typeof item === "string"
                            ? item
                            : JSON.stringify(item)
                        )}
                    </p>

                </div>

            `).join("")}

        </div>
    `;

}


/* ============================================================
   DASHBOARD
   ============================================================ */

async function loadDashboard() {

    if (!currentUser) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/dashboard"
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        updateDashboardStats(data);

        updateDashboardAlert(data);

        updateInventory(data);

        updatePriorityOrders(data);


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }

}


/* ------------------------------------------------------------
   DASHBOARD STATS
   ------------------------------------------------------------ */

function updateDashboardStats(data) {

    setText(
        "active-disruptions",
        data.active_disruptions ??
        data.active_cases ??
        0
    );


    setText(
        "orders-risk",
        data.orders_at_risk ??
        data.orders_risk ??
        0
    );


    setText(
        "stock-risk",
        data.stock_at_risk ??
        data.stock_risk ??
        0
    );


    setText(
        "suppliers-risk",
        data.suppliers_impacted ??
        data.suppliers_risk ??
        0
    );

}


/* ------------------------------------------------------------
   DASHBOARD ALERT
   ------------------------------------------------------------ */

function updateDashboardAlert(data) {

    const title =
        document.getElementById(
            "dashboard-alert-title"
        );

    const description =
        document.getElementById(
            "dashboard-alert-description"
        );


    if (!title || !description) {
        return;
    }


    const alert =
        data.current_priority ||
        data.priority ||
        data.alert;


    if (!alert) {

        title.textContent =
            "No active disruption";

        description.textContent =
            "Supply chain is currently operating normally.";

        return;

    }


    if (typeof alert === "string") {

        title.textContent =
            alert;

        description.textContent =
            "Review the disruption analysis for details.";

        return;

    }


    title.textContent =
        alert.title ||
        alert.name ||
        "Active disruption";


    description.textContent =
        alert.description ||
        alert.reason ||
        "Disruption requires attention.";

}


/* ------------------------------------------------------------
   INVENTORY
   ------------------------------------------------------------ */

function updateInventory(data) {

    const inventory =
        data.inventory ||
        data.stock_position ||
        {};


    const total =
        inventory.total_stock ??
        data.total_stock ??
        0;

    const reserved =
        inventory.reserved_stock ??
        data.reserved_stock ??
        0;

    const available =
        inventory.available_stock ??
        data.available_stock ??
        Math.max(
            total - reserved,
            0
        );


    setText(
        "total-stock",
        total
    );

    setText(
        "reserved-stock",
        reserved
    );

    setText(
        "available-stock",
        available
    );


    const reservedPercent =
        total > 0
        ? (reserved / total) * 100
        : 0;


    const availablePercent =
        total > 0
        ? (available / total) * 100
        : 0;


    setWidth(
        "total-stock-bar",
        100
    );

    setWidth(
        "reserved-stock-bar",
        reservedPercent
    );

    setWidth(
        "available-stock-bar",
        availablePercent
    );

}


/* ------------------------------------------------------------
   PRIORITY ORDERS
   ------------------------------------------------------------ */

function updatePriorityOrders(data) {

    const table =
        document.getElementById(
            "priority-orders-table"
        );


    if (!table) {
        return;
    }


    const orders =
        data.priority_orders ||
        data.orders_at_risk_list ||
        data.orders ||
        [];


    if (!Array.isArray(orders) || !orders.length) {

        table.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="empty-state">

                    No orders requiring attention.

                </td>

            </tr>
        `;

        return;

    }


    table.innerHTML =
        orders
        .slice(0, 8)
        .map(order => `

            <tr>

                <td>
                    ${escapeHtml(
                        order.order_id ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        order.customer ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        order.product_name ||
                        order.product_id ||
                        "-"
                    )}
                </td>

                <td>
                    ${order.quantity || 0}
                </td>

                <td>
                    ${escapeHtml(
                        order.priority ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        order.deadline ||
                        "-"
                    )}
                </td>

            </tr>

        `)
        .join("");

}


/* ============================================================
   HISTORY
   ============================================================ */

async function loadHistory() {

    const container =
        document.getElementById(
            "history-content"
        );


    if (!container || !currentUser) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/cases"
            );


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        const cases =
            Array.isArray(data)
            ? data
            : data.cases || [];


        if (!cases.length) {

            container.innerHTML = `

                <div class="empty-large">

                    <div>◷</div>

                    <h3>
                        No cases loaded
                    </h3>

                    <p>
                        Your analyzed cases will appear here.
                    </p>

                </div>
            `;

            return;

        }


        container.innerHTML = `

            <div class="panel">

                <div class="panel-heading">

                    <div>

                        <span class="panel-label">
                            CASE HISTORY
                        </span>

                        <h3>
                            Previously Analyzed Cases
                        </h3>

                    </div>

                </div>


                <div class="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>CASE</th>
                                <th>STATUS</th>
                                <th>SEVERITY</th>
                                <th>DATE</th>

                            </tr>

                        </thead>


                        <tbody>

                            ${cases.map(item => `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            item.case_id ||
                                            item.id ||
                                            "-"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.status ||
                                            "-"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.severity ||
                                            "-"
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.created_at ||
                                            item.timestamp ||
                                            "-"
                                        )}
                                    </td>

                                </tr>

                            `).join("")}

                        </tbody>

                    </table>

                </div>

            </div>
        `;


    } catch (error) {

        console.error(
            "History error:",
            error
        );

    }

}


/* ============================================================
   UTILITIES
   ============================================================ */

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }

}


function setWidth(id, value) {

    const element =
        document.getElementById(id);

    if (element) {

        element.style.width =
            Math.min(
                Math.max(value, 0),
                100
            ) + "%";

    }

}


function getSeverityClass(severity) {

    const value =
        String(severity || "")
        .toLowerCase();


    if (value.includes("critical")) {
        return "critical";
    }

    if (value.includes("high")) {
        return "warning";
    }

    if (value.includes("medium")) {
        return "warning";
    }

    return "";

}


function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }


    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* ============================================================
   TOAST
   ============================================================ */

function showToast(message) {

    const toast =
        document.getElementById(
            "toast"
        );

    const toastMessage =
        document.getElementById(
            "toast-message"
        );


    if (!toast || !toastMessage) {
        return;
    }


    toastMessage.textContent =
        message;


    toast.classList.add("show");


    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}

/* =========================================================
   DASHBOARD ANALYTICS
   ========================================================= */

function updateRiskChart(orders) {

    if (!Array.isArray(orders)) {
        return;
    }

    let critical = 0;
    let high = 0;
    let medium = 0;
    let low = 0;

    orders.forEach(order => {

        const priority =
            String(order.priority || "")
                .toLowerCase();

        if (priority === "critical") {
            critical++;
        }
        else if (priority === "high") {
            high++;
        }
        else if (priority === "medium") {
            medium++;
        }
        else {
            low++;
        }

    });

    const total =
        critical +
        high +
        medium +
        low;

    const max =
        Math.max(
            critical,
            high,
            medium,
            low,
            1
        );


    document.getElementById(
        "critical-count"
    ).textContent = critical;

    document.getElementById(
        "high-count"
    ).textContent = high;

    document.getElementById(
        "medium-count"
    ).textContent = medium;

    document.getElementById(
        "low-count"
    ).textContent = low;

    document.getElementById(
        "total-risk-orders"
    ).textContent = total;


    document.getElementById(
        "critical-bar"
    ).style.width =
        `${(critical / max) * 100}%`;

    document.getElementById(
        "high-bar"
    ).style.width =
        `${(high / max) * 100}%`;

    document.getElementById(
        "medium-bar"
    ).style.width =
        `${(medium / max) * 100}%`;

    document.getElementById(
        "low-bar"
    ).style.width =
        `${(low / max) * 100}%`;
}


/* =========================================================
   INVENTORY ANALYTICS
   ========================================================= */

function updateInventoryChart(
    total,
    reserved,
    available
) {

    total = Number(total) || 0;
    reserved = Number(reserved) || 0;
    available = Number(available) || 0;


    document.getElementById(
        "chart-total-stock"
    ).textContent = total;

    document.getElementById(
        "chart-reserved-stock"
    ).textContent = reserved;

    document.getElementById(
        "chart-available-stock"
    ).textContent = available;


    const percentage =
        total > 0
            ? Math.round(
                (available / total) * 100
            )
            : 0;


    document.getElementById(
        "inventory-available-percent"
    ).textContent =
        `${percentage}%`;


    const availableAngle =
        percentage * 3.6;


    document.querySelector(
        ".inventory-ring"
    ).style.background =
        `conic-gradient(
            #19a974 0deg,
            #19a974 ${availableAngle}deg,
            #e9eef4 ${availableAngle}deg,
            #e9eef4 360deg
        )`;
}