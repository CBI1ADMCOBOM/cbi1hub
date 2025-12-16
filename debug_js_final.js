    
        function logDebug(msg) {
            console.log(msg);
            const d = document.getElementById('debug-log');
            if (d) d.innerHTML += msg + "<br>";
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Carregar OPMs (Estações)
            fetch('/api/opms')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('opm_id');
                    select.innerHTML = '<option value="">Selecione a Estação...</option>';
                    data.forEach(opm => {
                        const option = document.createElement('option');
                        option.value = opm.id;
                        option.textContent = `${opm.EB} (${opm.GB})`;
                        select.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error('Erro ao carregar OPMs:', err);
                    document.getElementById('opm_id').innerHTML = '<option value="">Erro ao carregar</option>';
                    logDebug("Erro ao carregar OPMs: " + err);
                });

            // Carregar Naturezas RAIA
            fetch('/api/naturezas_raia')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('nature');
                    select.innerHTML = '<option value="">Selecione...</option>';
                    data.forEach(nat => {
                        const option = document.createElement('option');
                        option.value = nat.code;
                        option.textContent = nat.code;
                        select.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error('Erro ao carregar naturezas:', err);
                    document.getElementById('nature').innerHTML = '<option value="">Erro ao carregar</option>';
                });

            // Carregar Concessionárias
            fetch('/api/concessionarias')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('concessionaire_id');
                    select.innerHTML = '<option value="">Selecione...</option>';
                    data.forEach(css => {
                        const option = document.createElement('option');
                        option.value = css.id;
                        option.textContent = css.name;
                        select.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error('Erro ao carregar concessionárias:', err);
                    document.getElementById('concessionaire_id').innerHTML = '<option value="">Erro ao carregar</option>';
                });
        });

        // Lógica do GPS
        const btnGeo = document.getElementById('btn-geo');
        if (btnGeo) {
            btnGeo.addEventListener('click', () => {
                const btn = document.getElementById('btn-geo');
                const input = document.getElementById('location_text');
                const latInput = document.getElementById('latitude');
                const longInput = document.getElementById('longitude');

                if (!navigator.geolocation) {
                    alert('Geolocalização não suportada pelo seu navegador.');
                    return;
                }

                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Obtendo...';
                btn.disabled = true;

                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const long = position.coords.longitude;

                        // Preenche os campos ocultos
                        latInput.value = lat;
                        longInput.value = long;

                        // Preenche o campo visível
                        input.value = `${lat}, ${long}`;

                        btn.innerHTML = '<i class="bi bi-check-lg"></i> Sucesso';
                        setTimeout(() => {
                            btn.innerHTML = originalText;
                            btn.disabled = false;
                        }, 2000);
                    },
                    (error) => {
                        console.error(error);
                        alert('Erro ao obter localização. Verifique se o GPS está ativo e se você permitiu o acesso.');
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                    },
                    { enableHighAccuracy: true }
                );
            });
        }

        // Lógica do Responsável
        function toggleResponsibleFields() {
            const has = document.querySelector('input[name="has_responsible"]:checked');
            if (!has) return;
            const hasResponsible = has.value === 'YES';
            const detailsDiv = document.getElementById('responsible-details');
            const inputs = detailsDiv.querySelectorAll('input');

            if (hasResponsible) {
                detailsDiv.style.display = 'block';
                inputs.forEach(input => input.required = true);
            } else {
                detailsDiv.style.display = 'none';
                inputs.forEach(input => {
                    input.required = false;
                    input.value = ''; // Limpa os campos
                });
            }
        }

        // Inicializar estado correto
        document.addEventListener('DOMContentLoaded', () => {
            toggleResponsibleFields();
        });

        // --- MANAGE PHOTOS (ROBUST VERSION) ---
        window.uploadedFiles = []; 

        function initPhotoHandler() {
            const dropzone = document.getElementById('dropzone');
            const fileInput = document.getElementById('file-input');
            const gallery = document.getElementById('gallery');

            if (!dropzone || !fileInput) {
                console.error("Critical: Dropzone or Input not found");
                return;
            }

            // Drag & Drop events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-active'), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-active'), false);
            });

            dropzone.addEventListener('drop', handleDrop, false);
            fileInput.addEventListener('change', handleFiles, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                handleFiles({ target: { files: files } });
            }

            function handleFiles(e) {
                // Ensure files exists
                if (!e.target.files) return;
                
                const files = [...e.target.files];
                console.log("Files detected:", files.length);
                files.forEach(previewFile);
            }

            function previewFile(file) {
                console.log("Previewing:", file.name);
                window.uploadedFiles.push(file);

                const reader = new FileReader();
                
                reader.onload = function(e) {
                    console.log("File read successfully:", file.name);
                    const div = document.createElement('div');
                    div.className = 'preview-card';
                    div.innerHTML = `
                        <img src="${e.target.result}" alt="${file.name}">
                        <button type="button" class="delete-btn" title="Remover">
                            <i class="bi bi-x"></i>
                        </button>
                    `;
                    
                    // Add delete listener safely
                    const btn = div.querySelector('.delete-btn');
                    btn.onclick = function(ev) {
                        ev.preventDefault(); // Stop label trigger
                        ev.stopPropagation(); 
                        div.remove();
                        window.uploadedFiles = window.uploadedFiles.filter(f => f.name !== file.name);
                    };

                    gallery.appendChild(div);
                }

                reader.onerror = function() {
                    alert("Erro ao ler o arquivo " + file.name);
                }

                reader.readAsDataURL(file);
            }
        }

        // Init immediately if ready (since script is at bottom)
        initPhotoHandler();

        // Also listen for DOMContentLoaded just in case
        document.addEventListener('DOMContentLoaded', initPhotoHandler);

        // Validação e Envio do Formulário
        document.getElementById('occurrence-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            if (window.uploadedFiles.length === 0) {
                alert('Por favor, adicione pelo menos uma foto.');
                return;
            }

            const btn = e.target.querySelector('button[type="submit"]');
            const originalText = btn.textContent;
            btn.textContent = 'Enviando...';
            btn.disabled = true;

            const formData = new FormData(e.target);
            formData.delete('photos'); // Remove clean empty input

            window.uploadedFiles.forEach(file => {
                formData.append('photos', file);
            });

            try {
                const response = await fetch('/api/raia/save', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    alert('Sucesso! Redirecionando...');
                    window.location.href = '/elaborar-raia';
                } else {
                    alert('Erro: ' + (result.error || 'Erro desconhecido'));
                }
            } catch (error) {
                console.error(error);
                alert('Erro de conexão.');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    
