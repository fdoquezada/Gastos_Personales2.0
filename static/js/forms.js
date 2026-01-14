// static/js/forms.js - Manejo de formularios
document.addEventListener('DOMContentLoaded', function() {
    // Mostrar/ocultar campos según selecciones
    const dateRangeSelect = document.getElementById('date-range-select');
    const startDateField = document.getElementById('start-date');
    const endDateField = document.getElementById('end-date');
    
    if (dateRangeSelect && startDateField && endDateField) {
        function toggleDateFields() {
            const startDateContainer = startDateField.closest('.form-group, .col-md-6, .mb-3') || startDateField.parentElement;
            const endDateContainer = endDateField.closest('.form-group, .col-md-6, .mb-3') || endDateField.parentElement;
            
            if (dateRangeSelect.value === 'custom') {
                startDateContainer.style.display = 'block';
                endDateContainer.style.display = 'block';
            } else {
                startDateContainer.style.display = 'none';
                endDateContainer.style.display = 'none';
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
        preview.style.cssText = 'display: inline-block; width: 20px; height: 20px; border-radius: 4px; border: 1px solid #ddd;';
        select.parentNode.appendChild(preview);
        
        function updatePreview() {
            preview.style.backgroundColor = select.value;
        }
        
        select.addEventListener('change', updatePreview);
        updatePreview(); // Inicializar
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
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
    
    // Manejo de formularios modales
    const modalForms = document.querySelectorAll('.modal form');
    modalForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Opcional: Cerrar modal después de enviar
            const modal = this.closest('.modal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                setTimeout(() => {
                    if (modalInstance) modalInstance.hide();
                }, 1000);
            }
        });
    });
    
    // Prevenir doble envío de formularios
    const allForms = document.querySelectorAll('form');
    allForms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Procesando...';
                
                // Restaurar después de 5 segundos por si hay error
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    });
    
    // Formato de moneda en tiempo real
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            let value = this.value.replace(/[^0-9.]/g, '');
            if (value) {
                value = parseFloat(value).toFixed(2);
                this.value = value;
            }
        });
        
        input.addEventListener('focus', function() {
            this.value = this.value.replace(/[^0-9.]/g, '');
        });
    });
});

// static/js/forms.js - Funciones generales para formularios
document.addEventListener('DOMContentLoaded', function() {
    // Prevenir doble envío de formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                setTimeout(() => {
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });
    
    // Auto-seleccionar fecha de hoy si está vacía
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) {
            const today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
});