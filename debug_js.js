    
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
                });

            // Carregar Naturezas RAIA
            fetch('/api/naturezas_raia')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('nature');
                    select.innerHTML = '<option value="">Selecione...</option>';
                    data.forEach(nat => {
                        const option = document.createElement('option');
                        option.value = nat.code; // Usando o código como valor
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
        document.getElementById('btn-geo').addEventListener('click', () => {
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

        // Lógica do Responsável
        function toggleResponsibleFields() {
            const hasResponsible = document.querySelector('input[name="has_responsible"]:checked').value === 'YES';
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
        // Gerenciamento de Fotos
        let selectedFiles = []; // Array para armazenar os arquivos selecionados



        (function () {
            // DEBUG: Remover em produção
            console.log("Iniciando script de fotos...");

            const photoInput = document.getElementById('photos');
            if (photoInput) {
                console.log("Input #photos encontrado.");

                photoInput.addEventListener('change', (e) => {
                    alert("Evento de mudança detectado! Arquivos: " + e.target.files.length);
                    const files = Array.from(e.target.files);
                    console.log('Arquivos selecionados:', files.length);

                    files.forEach(file => {
                        alert("Processando: " + file.name);
                        selectedFiles.push(file);

                        const reader = new FileReader();
                        reader.onload = (ev) => {
                            const div = document.createElement('div');
                            div.className = 'photo-item';
                            div.style.position = 'relative';
                            div.style.width = '100px';
                            div.style.height = '100px';
                            div.style.border = '1px solid #ddd';
                            div.style.borderRadius = '4px';
                            div.style.overflow = 'hidden';

                            div.innerHTML = `
                                <img src="${ev.target.result}" style="width: 100%; height: 100%; object-fit: cover;">
                                <button type="button" class="btn-remove-photo" style="position: absolute; top: 2px; right: 2px; background: red; color: white; border: none; border-radius: 50%; width: 20px; height: 20px; font-size: 12px; cursor: pointer;">&times;</button>
                            `;

                            div.querySelector('.btn-remove-photo').addEventListener('click', () => {
                                const index = selectedFiles.indexOf(file);
                                if (index > -1) {
                                    selectedFiles.splice(index, 1);
                                }
                                div.remove();
                            });

                            document.getElementById('photo-preview-container').appendChild(div);
                        };
                        reader.onerror = (err) => {
                            console.error("Erro ao ler arquivo:", err);
                            alert("Erro ao processar imagem.");
                        };
                        reader.readAsDataURL(file);
                    });

                    e.target.value = '';
                });
            } else {
                console.error("Elemento #photos não encontrado!");
                alert("Erro interno: Input de fotos não encontrado.");
            }
        })();

        // Validação e Envio do Formulário
        document.getElementById('occurrence-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            if (selectedFiles.length === 0) {
                alert('Por favor, adicione pelo menos uma foto da ocorrência.');
                return;
            }

            const btn = e.target.querySelector('button[type="submit"]');
            const originalText = btn.textContent;
            btn.textContent = 'Enviando...';
            btn.disabled = true;

            const formData = new FormData(e.target);

            // Remove o campo 'photos' original vazio do FormData e adiciona os arquivos do array
            formData.delete('photos');
            selectedFiles.forEach(file => {
                formData.append('photos', file);
            });

            try {
                const response = await fetch('/api/raia/save', {
                    method: 'POST',
                    body: formData // Fetch envia multipart/form-data automaticamente
                });

                const result = await response.json();

                if (result.success) {
                    alert('Ocorrência registrada com sucesso! \n\nVocê pode visualizá-la no menu "VISUALIZAR", localizado ao lado da opção de gerar.');
                    window.location.href = '/elaborar-raia'; // Redireciona para o menu RAIA
                } else {
                    alert('Erro ao salvar: ' + (result.error || 'Erro desconhecido'));
                }
            } catch (error) {
                console.error(error);
                alert('Erro de conexão ao salvar ocorrência.');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
            }
        });
    
