const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000/index.html" : window.location.origin;

// Select DOM elements for Views
const btnPatientPortal = document.getElementById("btn-patient-portal");
const btnPharmacistConsole = document.getElementById("btn-pharmacist-console");
const btnAgentTrace = document.getElementById("btn-agent-trace");

const viewPatient = document.getElementById("view-patient");
const viewPharmacist = document.getElementById("view-pharmacist");
const viewTrace = document.getElementById("view-trace");

// Select DOM elements for general items
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const btnSend = document.getElementById("btn-send-message");
const btnVoice = document.getElementById("btn-voice-input");
const cartCounter = document.getElementById("cart-counter");
const cartCounterStat = document.getElementById("cart-counter-stat");
const lowStockCount = document.getElementById("low-stock-count");
const poCountStat = document.getElementById("po-count-stat");
const cartSummary = document.getElementById("cart-summary");
const btnClearCart = document.getElementById("btn-clear-cart");
const predictionTimeline = document.getElementById("prediction-timeline");
const inventoryTableBody = document.getElementById("inventory-table-body");
const poLogList = document.getElementById("po-log-list");
const traceConsole = document.getElementById("trace-console");
const btnResetDb = document.getElementById("btn-reset-db");
const btnRunAudit = document.getElementById("btn-run-audit");

// Prescription Upload elements
const prescriptionDropzone = document.getElementById("prescription-dropzone");
const prescriptionFileInput = document.getElementById("prescription-file-input");
const uploadFileInfo = document.getElementById("upload-file-info");

// Order Confirmation Modal elements
const btnPlaceOrder = document.getElementById("btn-place-order");
const orderConfirmModal = document.getElementById("order-confirm-modal");
const modalCartPreviewList = document.getElementById("modal-cart-preview-list");
const btnCancelOrder = document.getElementById("btn-cancel-order");
const btnCloseModalX = document.getElementById("btn-close-modal-x");
const btnSubmitOrderFinal = document.getElementById("btn-submit-order-final");

// Patient Order History container
const patientOrdersHistory = document.getElementById("patient-orders-history");

// Pharmacist Queue & Modals
const pharmacistVerificationQueue = document.getElementById("pharmacist-verification-queue");
const rxPreviewModal = document.getElementById("rx-preview-modal");
const rxPreviewMedsList = document.getElementById("rx-preview-meds-list");
const btnCloseRxModalX = document.getElementById("btn-close-rx-modal-x");
const btnCloseRxPreview = document.getElementById("btn-close-rx-preview");

// Safety Agent UI components
const safetyGuardWidget = document.getElementById("safety-guard-widget");
const safetyShieldWrapper = document.getElementById("safety-shield-wrapper");
const safetyShieldIcon = document.getElementById("safety-shield-icon");
const safetyStatusTitle = document.getElementById("safety-status-title");
const safetyStatusDesc = document.getElementById("safety-status-desc");
const chkPrescription = document.getElementById("chk-prescription");
const chkInteraction = document.getElementById("chk-interaction");

// Tab buttons inside Pharmacist Console
const tabInventory = document.getElementById("tab-inventory");
const tabProcurement = document.getElementById("tab-procurement");
const inventoryContent = document.getElementById("inventory-tab-content");
const procurementContent = document.getElementById("procurement-tab-content");

// Local state
let isVoiceListening = false;
let uploadedFileName = null;

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", () => {
    fetchInventory();
    fetchCart();
    fetchRefillTimeline();
    fetchPatientOrders();
    fetchPharmacistQueue();
    fetchDraftPOs();
    setupEventListeners();
});

function setupEventListeners() {
    // Sidebar Navigation Click Handlers
    btnPatientPortal.addEventListener("click", (e) => {
        e.preventDefault();
        setActiveView("patient");
    });

    btnPharmacistConsole.addEventListener("click", (e) => {
        e.preventDefault();
        setActiveView("pharmacist");
        fetchInventory();
        fetchPharmacistQueue();
        fetchDraftPOs();
    });

    btnAgentTrace.addEventListener("click", (e) => {
        e.preventDefault();
        setActiveView("trace");
    });

    // Chat Submit
    btnSend.addEventListener("click", handleSendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleSendMessage();
    });

    // Voice Simulation
    btnVoice.addEventListener("click", handleVoiceSimulation);

    // Clear Cart
    btnClearCart.addEventListener("click", handleClearCart);

    // Reset DB
    btnResetDb.addEventListener("click", handleResetDb);

    // Procurement Manual Run Audit
    btnRunAudit.addEventListener("click", () => {
        setActiveView("patient");
        sendQuickMessage("Show inventory stock status and auto reorder");
    });

    // Drag and Drop Upload Handlers
    prescriptionDropzone.addEventListener("click", () => {
        prescriptionFileInput.click();
    });

    prescriptionDropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        prescriptionDropzone.style.borderColor = "var(--primary)";
    });

    prescriptionDropzone.addEventListener("dragleave", () => {
        prescriptionDropzone.style.borderColor = "rgba(255, 255, 255, 0.15)";
    });

    prescriptionDropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        prescriptionDropzone.style.borderColor = "rgba(255, 255, 255, 0.15)";
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    prescriptionFileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    // Place Order Modal Triggers
    btnPlaceOrder.addEventListener("click", handleOpenOrderModal);
    btnCancelOrder.addEventListener("click", () => orderConfirmModal.classList.add("hidden"));
    btnCloseModalX.addEventListener("click", () => orderConfirmModal.classList.add("hidden"));
    btnSubmitOrderFinal.addEventListener("click", handleSubmitOrderFinal);

    // Verification Queue Viewer Closing
    btnCloseRxModalX.addEventListener("click", () => rxPreviewModal.classList.add("hidden"));
    btnCloseRxPreview.addEventListener("click", () => rxPreviewModal.classList.add("hidden"));

    // Tabs toggle inside Pharmacist Console
    tabInventory.addEventListener("click", () => {
        tabInventory.classList.add("active");
        tabProcurement.classList.remove("active");
        inventoryContent.classList.remove("hidden");
        procurementContent.classList.add("hidden");
    });

    tabProcurement.addEventListener("click", () => {
        tabProcurement.classList.add("active");
        tabInventory.classList.remove("active");
        procurementContent.classList.remove("hidden");
        inventoryContent.classList.add("hidden");
    });
}

// Function to handle showing/hiding main sections
function setActiveView(view) {
    btnPatientPortal.classList.remove("active");
    btnPharmacistConsole.classList.remove("active");
    btnAgentTrace.classList.remove("active");

    viewPatient.classList.add("hidden");
    viewPharmacist.classList.add("hidden");
    viewTrace.classList.add("hidden");

    if (view === "patient") {
        btnPatientPortal.classList.add("active");
        viewPatient.classList.remove("hidden");
    } else if (view === "pharmacist") {
        btnPharmacistConsole.classList.add("active");
        viewPharmacist.classList.remove("hidden");
    } else if (view === "trace") {
        btnAgentTrace.classList.add("active");
        viewTrace.classList.remove("hidden");
    }
}

// Fetch Inventory Stock Levels
async function fetchInventory() {
    try {
        const res = await fetch(`${API_BASE}/api/inventory`);
        const data = await res.json();
        renderInventory(data.inventory);
        updateLowStockStats(data.inventory);
    } catch (err) {
        console.error("Error fetching inventory:", err);
    }
}

// Update low stock stats indicators
function updateLowStockStats(inventory) {
    const lowCount = inventory.filter(item => item.status === "Low Stock").length;
    lowStockCount.innerText = `${lowCount} Low ${lowCount === 1 ? 'Item' : 'Items'}`;

    const card = document.getElementById("low-stock-stat-card");
    if (lowCount > 0) {
        card.classList.add("pulse-glow-red");
    } else {
        card.classList.remove("pulse-glow-red");
    }
}

// Render Inventory Table
function renderInventory(inventory) {
    inventoryTableBody.innerHTML = "";
    inventory.forEach(item => {
        const row = document.createElement("tr");

        const statusClass = item.status === "Low Stock" ? "warning" : "good";
        const statusIcon = item.status === "Low Stock" ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        const isRxLabel = item.is_rx ? '<span class="category-tag text-danger">Rx Only</span>' : '<span class="category-tag text-success">OTC</span>';

        row.innerHTML = `
            <td><strong>${item.name}</strong></td>
            <td>${item.quantity} units</td>
            <td>${item.reorder_threshold} units</td>
            <td>$${item.price.toFixed(2)}</td>
            <td>${isRxLabel}</td>
            <td><span class="badge-status ${statusClass}">${statusIcon} ${item.status}</span></td>
        `;
        inventoryTableBody.appendChild(row);
    });
}

// Fetch Shopping Cart Status
async function fetchCart() {
    try {
        const res = await fetch(`${API_BASE}/api/cart`);
        const data = await res.json();
        renderCart(data);
    } catch (err) {
        console.error("Error fetching cart:", err);
    }
}

// Render Shopping Cart Summary
function renderCart(cart) {
    cartCounter.innerText = `${cart.total_items_count} items`;
    cartCounterStat.innerText = `${cart.total_items_count} ${cart.total_items_count === 1 ? 'Item' : 'Items'}`;

    if (cart.cart_items.length === 0) {
        cartSummary.innerHTML = `
            <div class="empty-cart-state">
                <i class="fa-solid fa-basket-shopping"></i>
                <p>Your shopping cart is currently empty.</p>
            </div>
        `;
        btnPlaceOrder.disabled = true;
        return;
    }

    btnPlaceOrder.disabled = false;
    let html = '<div class="cart-items-list" style="display: flex; flex-direction: column; gap: 8px;">';
    cart.cart_items.forEach(item => {
        html += `
            <div class="cart-item-row">
                <div>
                    <span class="cart-item-name">${item.medicine_name}</span>
                    <span class="cart-item-qty">x${item.quantity}</span>
                </div>
                <span class="cart-item-price">$${item.total_price.toFixed(2)}</span>
            </div>
        `;
    });

    html += `
        </div>
        <div class="card-divider" style="margin: 10px 0 5px 0;"></div>
        <div class="cart-totals">
            <span>Total Amount:</span>
            <span class="cart-item-price" style="font-size: 16px; font-weight: 800;">$${cart.total_amount.toFixed(2)}</span>
        </div>
    `;
    cartSummary.innerHTML = html;
}

// Handle Prescription Mock Upload
async function handleFileUpload(file) {
    uploadedFileName = file.name;
    uploadFileInfo.innerText = `Uploaded: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

    // Add message and trigger parser
    appendMessage("user", `[Uploaded Prescription Document: ${file.name}]`);
    const loaderId = appendTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/upload-prescription`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ filename: file.name, customer_id: "cust_101" })
        });
        const data = await res.json();

        removeTypingIndicator(loaderId);
        appendMessage("system", data.response);

        appendTraces(data.traces);
        highlightActiveAgentNode(data.traces);
        updateSafetyAgentWidget(data.response, data.traces);

        renderCart(data.cart);
        renderInventory(data.inventory);
        updateLowStockStats(data.inventory);

    } catch (err) {
        removeTypingIndicator(loaderId);
        appendMessage("system", "Error processing prescription document.");
        console.error(err);
    }
}

// Open Order Placement Modal
async function handleOpenOrderModal() {
    try {
        const res = await fetch(`${API_BASE}/api/cart`);
        const cart = await res.json();

        if (cart.cart_items.length === 0) return;

        modalCartPreviewList.innerHTML = "";
        cart.cart_items.forEach(item => {
            const div = document.createElement("div");
            div.className = "modal-cart-preview-item";
            div.innerHTML = `
                <span>${item.medicine_name} x${item.quantity}</span>
                <span>$${item.total_price.toFixed(2)}</span>
            `;
            modalCartPreviewList.appendChild(div);
        });

        orderConfirmModal.classList.remove("hidden");
    } catch (err) {
        console.error(err);
    }
}

// Submit Order Final
async function handleSubmitOrderFinal() {
    orderConfirmModal.classList.add("hidden");
    const loaderId = appendTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/confirm-order`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_id: "cust_101",
                prescription_file: uploadedFileName || "uploaded_rx.pdf"
            })
        });
        const result = await res.json();

        removeTypingIndicator(loaderId);

        if (result.status === "success") {
            appendMessage("system", `🎉 **Order Submitted Successfully!**\n\n${result.message}`);

            // Clear uploader state
            uploadedFileName = null;
            uploadFileInfo.innerText = "Simulates OCR parsing upon upload";

            // Refresh cart, history list, and pharmacist list
            fetchCart();
            fetchPatientOrders();
            fetchPharmacistQueue();

            // Append system trace
            appendTraces([{
                agent: "System",
                message: `Order #${result.order.id} loaded into Pharmacist Verification Queue. Status: Awaiting Verification.`,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
        } else {
            appendMessage("system", `Failed to place order: ${result.message}`);
        }
    } catch (err) {
        removeTypingIndicator(loaderId);
        appendMessage("system", "Network error submitting order.");
        console.error(err);
    }
}

// Fetch Patient Order History (User portal)
async function fetchPatientOrders() {
    try {
        const res = await fetch(`${API_BASE}/api/orders?customer_id=cust_101`);
        const orders = await res.json();
        renderPatientOrders(orders);
    } catch (err) {
        console.error(err);
    }
}

function renderPatientOrders(orders) {
    if (orders.length === 0) {
        patientOrdersHistory.innerHTML = `
            <div class="empty-orders-state">
                <i class="fa-solid fa-receipt"></i>
                <p>No orders placed yet.</p>
            </div>
        `;
        return;
    }

    patientOrdersHistory.innerHTML = "";
    orders.forEach(order => {
        const div = document.createElement("div");
        div.className = "order-history-item";

        // Build items descriptive text
        const itemsText = order.items.map(i => `${i.medicine_name} (x${i.quantity})`).join(", ");
        const statusBadgeClass = order.status === "Pending Verification" ? "badge-status warning" : "badge-status good";
        const statusIcon = order.status === "Pending Verification" ? '<i class="fa-solid fa-clock"></i>' : '<i class="fa-solid fa-circle-check"></i>';

        div.innerHTML = `
            <div class="order-history-header">
                <span class="order-history-id">Order #${order.id}</span>
                <span class="order-history-date">${order.order_date}</span>
            </div>
            <div class="order-history-items-list">${itemsText}</div>
            <div class="order-history-footer">
                <span class="${statusBadgeClass}">${statusIcon} ${order.status}</span>
                <span class="order-history-price">$${order.total_price.toFixed(2)}</span>
            </div>
        `;
        patientOrdersHistory.appendChild(div);
    });
}

// Fetch Pharmacist Verification Queue
async function fetchPharmacistQueue() {
    try {
        const res = await fetch(`${API_BASE}/api/orders`);
        const orders = await res.json();
        renderPharmacistQueue(orders);
    } catch (err) {
        console.error(err);
    }
}

function renderPharmacistQueue(orders) {
    // Filter only pending verification orders
    const pending = orders.filter(o => o.status === "Pending Verification");

    if (pending.length === 0) {
        pharmacistVerificationQueue.innerHTML = `
            <div class="empty-queue-state">
                <i class="fa-solid fa-circle-check" style="font-size: 28px; color: var(--success);"></i>
                <p>Verification queue is empty. Awaiting patient orders.</p>
            </div>
        `;
        return;
    }

    pharmacistVerificationQueue.innerHTML = "";
    pending.forEach(order => {
        const div = document.createElement("div");
        div.className = "queue-item";

        const itemsHtml = order.items.map(i => `• <strong>${i.medicine_name}</strong> (Qty: ${i.quantity})`).join("<br>");
        const fileAttachment = order.prescription_file || "uploaded_prescription.pdf";

        div.innerHTML = `
            <div class="queue-item-header">
                <span class="queue-item-title">Patient Order #${order.id}</span>
                <span class="order-history-date">Awaiting verification</span>
            </div>
            <div class="queue-item-meds">
                ${itemsHtml}
            </div>
            <div class="queue-item-attachment" onclick="viewPrescriptionPreview(${order.id})">
                <i class="fa-solid fa-file-pdf"></i> View Attachment: ${fileAttachment}
            </div>
            <div class="queue-item-actions">
                <button class="btn-queue-action view" onclick="viewPrescriptionPreview(${order.id})">
                    <i class="fa-solid fa-magnifying-glass"></i> View Rx
                </button>
                <button class="btn-queue-action dispatch" onclick="dispatchOrder(${order.id})">
                    <i class="fa-solid fa-truck-fast"></i> Verify & Dispatch
                </button>
            </div>
        `;
        pharmacistVerificationQueue.appendChild(div);
    });
}

// Pharmacist views uploaded prescription document mock
async function viewPrescriptionPreview(orderId) {
    try {
        const res = await fetch(`${API_BASE}/api/orders`);
        const orders = await res.json();
        const order = orders.find(o => o.id === orderId);

        if (!order) return;

        rxPreviewMedsList.innerHTML = "";
        order.items.forEach(item => {
            const p = document.createElement("p");
            p.innerHTML = `Rx: <strong>${item.medicine_name}</strong> • Qty: ${item.quantity}<br><small>Sig: Take as directed in user dosage instructions.</small>`;
            rxPreviewMedsList.appendChild(p);
        });

        rxPreviewModal.classList.remove("hidden");
    } catch (err) {
        console.error(err);
    }
}

// Pharmacist dispatches order
async function dispatchOrder(orderId) {
    try {
        const res = await fetch(`${API_BASE}/api/dispatch-order`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ order_id: orderId })
        });
        const result = await res.json();

        if (result.status === "success") {
            alert(`Order #${orderId} verified and dispatched successfully.`);

            // Refresh queues and lists
            fetchPharmacistQueue();
            fetchInventory();
            fetchPatientOrders();
            fetchDraftPOs();

            // Add system trace log
            appendTraces([{
                agent: "System",
                message: `Order #${orderId} verified and successfully dispatched. Inventory stock levels updated in SQLite database.`,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);

            // If any item fell below threshold, Procurement Agent logs traces
            if (result.low_stock_alerts.length > 0) {
                const alerts = result.low_stock_alerts.map(a => `${a.medicine_name} (${a.stock_left} left)`).join(", ");
                appendTraces([{
                    agent: "ProcurementAgent",
                    message: `ALERT: Low Stock levels detected on dispatch: [${alerts}]. Draft supplier POs compiled.`,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                }]);

                // Switch tabs in console to show PO Center alerts
                tabProcurement.click();
            }
        } else {
            alert(`Dispatch Error: ${result.message}`);
        }
    } catch (err) {
        alert("Error dispatching order.");
        console.error(err);
    }
}

// Fetch Draft POs generated by Procurement Agent
async function fetchDraftPOs() {
    try {
        const res = await fetch(`${API_BASE}/api/procurement/drafts`);
        const drafts = await res.json();
        renderDraftPOs(drafts);
    } catch (err) {
        console.error(err);
    }
}

function renderDraftPOs(drafts) {
    const list = drafts;
    poCountStat.innerText = `${list.length} POs`;

    if (list.length === 0) {
        poLogList.innerHTML = `
            <div class="empty-po-state">
                <i class="fa-solid fa-truck-moving"></i>
                <p>No procurement purchase orders triggered yet. Stock levels are above thresholds.</p>
            </div>
        `;
        return;
    }

    poLogList.innerHTML = "";
    list.forEach(po => {
        const div = document.createElement("div");
        div.className = "po-item";

        let statusBadgeColor = po.status === "Invoiced" ? "po-badge bg-good" : "po-badge";
        let isDraft = po.status === "Draft - Awaiting Confirmation";

        let actionsHtml = "";
        if (isDraft) {
            actionsHtml = `
                <div class="po-email-input-wrapper">
                    <input type="email" class="po-email-input" id="email-${po.id}" value="${po.supplier_email}" placeholder="Supplier Email">
                    <button class="btn-po-confirm" onclick="confirmPO('${po.item}', '${po.id}')">
                        <i class="fa-solid fa-envelope"></i> Confirm & Send
                    </button>
                </div>
            `;
        }

        div.innerHTML = `
            <div style="width: 100%; display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="po-title">PO: ${po.item} (Qty: ${po.quantity_to_order})</span>
                    <span class="${statusBadgeColor}">${po.status}</span>
                </div>
                <span class="po-desc">ID: ${po.id} • Wholesaler cost: $${po.wholesale_cost.toFixed(2)}</span>
                ${actionsHtml}
            </div>
        `;
        poLogList.appendChild(div);
    });
}

// Confirm PO & Email supplier
async function confirmPO(itemName, poId) {
    const emailField = document.getElementById(`email-${poId}`);
    const email = emailField.value.trim();

    if (!email) {
        alert("Please enter a valid supplier email address.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/api/procurement/confirm`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item: itemName, supplier_email: email })
        });
        const result = await res.json();

        if (result.status === "success") {
            alert(`PO confirmed. Invoice successfully emailed to ${email}. stock restocked.`);

            // Refresh lists
            fetchDraftPOs();
            fetchInventory();

            // Log ProcurementAgent trace
            appendTraces([{
                agent: "ProcurementAgent",
                message: `Invoice confirmed and successfully emailed to supplier '${email}'. Wholesaler restocked 50 units. Database inventory updated.`,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }]);
        } else {
            alert(`PO Confirmation Error: ${result.message}`);
        }
    } catch (err) {
        alert("Error confirming PO.");
        console.error(err);
    }
}

// Fetch Depletion Timelines & Refills (Forecast Agent)
async function fetchRefillTimeline() {
    try {
        renderTimeline();
    } catch (err) {
        console.error("Error fetching timeline:", err);
    }
}

// Render Timeline
function renderTimeline() {
    const items = [
        { name: "Lisinopril 10mg", daysLeft: 0, status: "Refill Needed Now", class: "red", percent: 0, desc: "Takes 1 tablet daily. Runout date: June 27, 2026 (Today)" },
        { name: "Metformin 500mg", daysLeft: 5, status: "Refill in 5 days", class: "orange", percent: 20, desc: "Takes 2 tablets daily. Runout date: July 02, 2026" },
        { name: "Atorvastatin 20mg", daysLeft: 0, status: "Out of Stock", class: "red", percent: 0, desc: "Takes 1 tablet at bedtime. Runout date: June 27, 2026 (Today)" }
    ];

    predictionTimeline.innerHTML = "";
    items.forEach(item => {
        const div = document.createElement("div");
        div.className = "timeline-item";

        div.innerHTML = `
            <div class="med-details">
                <span class="name">${item.name}</span>
                <span class="history-info">${item.desc}</span>
            </div>
            <div class="timeline-progress">
                <span class="text-${item.class}">${item.status}</span>
                <div class="progress-bar-container">
                    <div class="progress-fill ${item.class}" style="width: ${item.percent}%"></div>
                </div>
            </div>
        `;
        predictionTimeline.appendChild(div);
    });
}

// Handle Send Chat Message
async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";
    appendMessage("user", text);

    const loaderId = appendTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, customer_id: "cust_101" })
        });
        const data = await res.json();

        removeTypingIndicator(loaderId);
        appendMessage("system", data.response);

        appendTraces(data.traces);
        highlightActiveAgentNode(data.traces);
        updateSafetyAgentWidget(data.response, data.traces);

        renderCart(data.cart);
        renderInventory(data.inventory);
        updateLowStockStats(data.inventory);

        // Auto-extract POs if the user triggered procurement via chat
        fetchDraftPOs();

    } catch (err) {
        removeTypingIndicator(loaderId);
        appendMessage("system", "Error communicating with Mediloon Agent System. Please ensure the backend app is running (run 'python backend/app.py' in your terminal).");
        console.error(err);
    }
}

// Update the Safety Agent status panel on the right side
function updateSafetyAgentWidget(response, traces) {
    const hasBlocked = response.includes("Blocked") || response.includes("🛑") || response.includes("Safety Block") || response.includes("Block");

    if (hasBlocked) {
        safetyShieldWrapper.className = "shield-icon-wrapper warning";
        safetyShieldIcon.className = "fa-solid fa-triangle-exclamation";
        safetyStatusTitle.innerText = "Safety Alert: Blocked";

        if (response.includes("prescription") || response.includes("Prescription")) {
            safetyStatusDesc.innerText = "Order blocked: Missing or expired prescription.";
            chkPrescription.innerHTML = '<i class="fa-solid fa-circle-xmark text-danger"></i> <span>Prescription Verification</span>';
            chkInteraction.innerHTML = '<i class="fa-solid fa-circle-check text-success"></i> <span>Drug-Drug Interaction Scan</span>';
        } else if (response.includes("interaction") || response.includes("Interaction")) {
            safetyStatusDesc.innerText = "Order blocked: High-risk drug-drug interaction.";
            chkPrescription.innerHTML = '<i class="fa-solid fa-circle-check text-success"></i> <span>Prescription Verification</span>';
            chkInteraction.innerHTML = '<i class="fa-solid fa-circle-xmark text-danger"></i> <span>Drug-Drug Interaction Scan</span>';
        } else {
            safetyStatusDesc.innerText = "Safety checks failed. Transaction terminated.";
            chkPrescription.innerHTML = '<i class="fa-solid fa-circle-xmark text-danger"></i> <span>Prescription Verification</span>';
            chkInteraction.innerHTML = '<i class="fa-solid fa-circle-xmark text-danger"></i> <span>Drug-Drug Interaction Scan</span>';
        }
    } else {
        safetyShieldWrapper.className = "shield-icon-wrapper safe";
        safetyShieldIcon.className = "fa-solid fa-shield-halved";
        safetyStatusTitle.innerText = "System Status: Safe";
        safetyStatusDesc.innerText = "All active safety evaluations passed.";
        chkPrescription.innerHTML = '<i class="fa-solid fa-circle-check text-success"></i> <span>Prescription Verification</span>';
        chkInteraction.innerHTML = '<i class="fa-solid fa-circle-check text-success"></i> <span>Drug-Drug Interaction Scan</span>';
    }
}

// Highlight Node Diagram depending on which agent ran
function highlightActiveAgentNode(traces) {
    const nodes = ["patient", "ordering", "safety", "forecast", "procurement", "db"];
    nodes.forEach(n => document.getElementById(`node-${n}`).classList.remove("active"));

    if (!traces || traces.length === 0) {
        document.getElementById("node-patient").classList.add("active");
        return;
    }

    const lastTrace = traces[traces.length - 1];
    const agent = lastTrace.agent;

    if (agent === "OrderingAgent") {
        document.getElementById("node-ordering").classList.add("active");
    } else if (agent === "SafetyAgent") {
        document.getElementById("node-safety").classList.add("active");
    } else if (agent === "ForecastAgent") {
        document.getElementById("node-forecast").classList.add("active");
    } else if (agent === "ProcurementAgent") {
        document.getElementById("node-procurement").classList.add("active");
    } else {
        document.getElementById("node-patient").classList.add("active");
    }

    document.getElementById("node-db").classList.add("active");
}

// Append Chat Message to screen
function appendMessage(sender, text) {
    const div = document.createElement("div");
    div.className = `message ${sender}`;

    const avatarIcon = sender === "user" ? "fa-user" : "fa-robot";
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    div.innerHTML = `
        <div class="msg-avatar">
            <i class="fa-solid ${avatarIcon}"></i>
        </div>
        <div class="msg-bubble">
            ${formatMarkdown(text)}
            <div class="msg-time">${time}</div>
        </div>
    `;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Append typing indicator
function appendTypingIndicator() {
    const id = `typing-${Date.now()}`;
    const div = document.createElement("div");
    div.id = id;
    div.className = "message system";
    div.innerHTML = `
        <div class="msg-avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="msg-bubble" style="padding: 12px 20px;">
            <i class="fa-solid fa-ellipsis fa-bounce"></i> Thinking...
        </div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Send Quick prompt chip
function sendQuickMessage(text) {
    chatInput.value = text;
    handleSendMessage();
}

// Format Markdown Bold / Code strings
function formatMarkdown(text) {
    let formatted = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
}

// Append Agent Trace Logs to Terminal Console
function appendTraces(traces) {
    if (!traces || traces.length === 0) return;

    const placeholder = traceConsole.querySelector(".trace-placeholder");
    if (placeholder) placeholder.remove();

    traces.forEach(trace => {
        const div = document.createElement("div");
        div.className = `trace-line ${trace.agent}`;
        div.innerHTML = `
            <div class="trace-header">
                <span class="trace-agent ${trace.agent}">[${trace.agent}]</span>
                <span class="trace-time">${trace.timestamp}</span>
            </div>
            <div class="trace-msg">&gt;&gt; ${trace.message}</div>
        `;
        traceConsole.appendChild(div);
    });

    traceConsole.scrollTop = traceConsole.scrollHeight;
}

// Simulate Voice Input
function handleVoiceSimulation() {
    if (isVoiceListening) return;

    isVoiceListening = true;
    btnVoice.classList.add("listening");
    btnVoice.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    chatInput.placeholder = "Listening to voice input...";

    const voiceCommands = [
        "Order Lisinopril 10mg",
        "Add 2 Paracetamol 500mg to my cart",
        "When will my chronic medicines run out?",
        "Check store stock status and auto reorder",
        "Order Warfarin 5mg"
    ];

    const randomCommand = voiceCommands[Math.floor(Math.random() * voiceCommands.length)];

    setTimeout(() => {
        btnVoice.classList.remove("listening");
        btnVoice.innerHTML = '<i class="fa-solid fa-microphone"></i>';
        chatInput.value = randomCommand;
        chatInput.placeholder = "Ask Mediloon or request medicine refills...";
        isVoiceListening = false;

        handleSendMessage();
    }, 2000);
}

// Clear cart
async function handleClearCart() {
    try {
        const res = await fetch(`${API_BASE}/api/clear-cart`, { method: "POST" });
        const data = await res.json();
        renderCart(data.cart);
        updateSafetyAgentWidget("Safe", []);
        appendMessage("system", "Shopping cart cleared.");
    } catch (err) {
        console.error(err);
    }
}

// Reset System Database
async function handleResetDb() {
    if (!confirm("Are you sure you want to reset the system? This will clear the cart, restore original stock levels, and reset all order histories.")) return;

    try {
        const res = await fetch(`${API_BASE}/api/reset-db`, { method: "POST" });
        const data = await res.json();

        fetchInventory();
        fetchCart();
        renderTimeline();

        // Reset logs and queue states
        fetchPatientOrders();
        fetchPharmacistQueue();
        fetchDraftPOs();

        traceConsole.innerHTML = `
            <div class="trace-placeholder">
                <i class="fa-solid fa-code"></i>
                <p>Interactive agent traces will display here during checkout, forecasting, and safety audits.</p>
            </div>
        `;

        appendTraces([{
            agent: "System",
            message: "Database schema successfully re-initialized and seeded.",
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);

        updateSafetyAgentWidget("Safe", []);
        highlightActiveAgentNode([]);

        alert(data.message);
    } catch (err) {
        console.error(err);
    }
}
