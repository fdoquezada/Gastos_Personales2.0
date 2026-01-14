// Main JavaScript file for the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Format currency inputs
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });
    
    // Confirm before delete actions
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que deseas eliminar este elemento? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });
    
    // Update current month display
    function updateCurrentMonth() {
        const now = new Date();
        const months = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ];
        const currentMonth = months[now.getMonth()] + ' ' + now.getFullYear();
        
        const monthElements = document.querySelectorAll('.current-month');
        monthElements.forEach(el => {
            el.textContent = currentMonth;
        });
    }
    
    // Call update on page load
    updateCurrentMonth();
    
    // Auto-update every hour
    setInterval(updateCurrentMonth, 3600000);
    
    // Toggle sidebar on mobile
    const sidebarToggler = document.getElementById('sidebarToggler');
    if (sidebarToggler) {
        sidebarToggler.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('show');
        });
    }
});

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN',
        minimumFractionDigits: 2
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-MX', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// static/js/forms.js
document.addEventListener('DOMContentLoaded', function() {
    // Mostrar/ocultar campos según selecciones
    const dateRangeSelect = document.getElementById('date-range-select');
    const startDateField = document.getElementById('start-date');
    const endDateField = document.getElementById('end-date');
    
    if (dateRangeSelect) {
        function toggleDateFields() {
            if (dateRangeSelect.value === 'custom') {
                startDateField.parentElement.style.display = 'block';
                endDateField.parentElement.style.display = 'block';
            } else {
                startDateField.parentElement.style.display = 'none';
                endDateField.parentElement.style.display = 'none';
            }
        }
        
        dateRangeSelect.addEventListener('change', toggleDateFields);
        toggleDateFields(); // Ejecutar al cargar
    }
    
    // Previsualización de color en categorías
    const colorSelects = document.querySelectorAll('select[name="color"]');
    colorSelects.forEach(select => {
        const preview = document.createElement('span');
        preview.className = 'color-preview ms-2';
        preview.style.cssText = `
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 1px solid #ddd;
        `;
        select.parentNode.appendChild(preview);
        
        function updatePreview() {
            preview.style.backgroundColor = select.value;
        }
        
        select.addEventListener('change', updatePreview);
        updatePreview(); // Inicializar
        
        // También para el modal
        if (select.closest('.modal')) {
            const modal = select.closest('.modal');
            modal.addEventListener('shown.bs.modal', updatePreview);
        }
    });
    
    // Validación de montos positivos
    const amountInputs = document.querySelectorAll('input[type="number"][min="0"]');
    amountInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (parseFloat(this.value) < 0) {
                this.value = 0;
            }
        });
    });
    
    // Auto-completar fecha actual
    const dateInputs = document.querySelectorAll('input[type="date"]:not([value])');
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = new Date().toISOString().split('T')[0];
        }
    });
    
    // Manejo de formularios modales
    const modalForms = document.querySelectorAll('.modal form');
    modalForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Cerrar modal después de enviar
            const modal = this.closest('.modal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                setTimeout(() => {
                    modalInstance.hide();
                }, 500);
            }
        });
    });
    
    // Prevenir doble envío de formularios
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Procesando...';
            }
        });
    });
});