/**
 * Inclui o conteúdo de arquivos HTML em outros arquivos HTML.
 * @param {string} filename O nome do arquivo HTML (ex: 'Estilos').
 * @return {string} O conteúdo do arquivo.
 */
function include(filename) {
  return HtmlService.createTemplateFromFile(filename).evaluate().getContent();
}

/**
 * Abre o formulário principal como Aplicativo Web.
 */
function doGet() {
  return HtmlService.createTemplateFromFile('Formulario').evaluate()
      .setTitle('Gerador de Relatório de Destaque')
      .setSandboxMode(HtmlService.SandboxMode.IFRAME);
}

/**
 * Processa os dados recebidos do formulário e gera o texto padronizado.
 * @param {Object} dados - Um objeto com os dados do formulário.
 * @return {string} O texto formatado.
 */
function gerarRelatorio(dados) {
  // Certifica-se de que a hora de término só é usada se o status for ENCERRADA
  let dataHoraTermino = '';
  if (dados.statusTermino === 'ENCERRADA' && dados.dataTermino && dados.horaTermino) {
      // Formata a data de AAAA-MM-DD para DD/MM/AAAA
      const dataFormatada = dados.dataTermino.split('-').reverse().join('/');
      dataHoraTermino = `DATA/HORÁRIO DO TÉRMINO: ${dataFormatada} às ${dados.horaTermino}h`;
  } else {
      dataHoraTermino = `STATUS: ${dados.statusTermino}`;
  }
  
  // K. ENCARREGADO NO LOCAL: Concatena a patente/graduação com o QRA
  const encarregadoLocal = dados.rankEncarregadoLocal && dados.nomeEncarregadoLocal
    ? `${dados.rankEncarregadoLocal} ${dados.nomeEncarregadoLocal}`
    : dados.rankEncarregadoLocal;
    
  // N. NOME PM TRANSMISSÃO: Concatena a patente/graduação com o QRA
  const pmTransmissao = dados.rankPmTransmissao && dados.nomePmTransmissao
    ? `${dados.rankPmTransmissao} ${dados.nomePmTransmissao}`
    : dados.rankPmTransmissao;
    
  // P. OFICIAIS QUE COMPARECERAM NO LOCAL: Concatena a patente/graduação com o QRA
  const oficiaisLocal = dados.rankOficiaisLocal && dados.nomeOficiaisLocal
    ? `${dados.rankOficiaisLocal} ${dados.nomeOficiaisLocal}`
    : dados.rankOficiaisLocal;

  const output = `
*SECRETARIA DA SEGURANÇA PÚBLICA* 
*CORPO DE BOMBEIROS MILITAR DO ESTADO DE SÃO PAULO*
${dados.gb} - ${dados.sgb} - ${dados.estacaoAtendimento}
*A. NÚMERO OCORRÊNCIA*: ${dados.numOcorrencia}
*B. DATA/HORA DA OCORRÊNCIA*: *${dados.dataOcorrencia.split('-').reverse().join('/')} às ${dados.horaOcorrencia}h*
*C. ${dataHoraTermino}*
*D. TIPO DE OCORRÊNCIA (JUSTIFICATIVA VULTO/DESTAQUE):* ${dados.tipoOcorrencia}
*E. NATUREZA DA OCORRÊNCIA:* ${dados.natureza}
*F. MUNICÍPIO:* ${dados.municipio}
*G. ENDEREÇO:* ${dados.endereco}
*H. BAIRRO:* ${dados.bairro || 'N/I'}
*I. QUANTIDADE DE VIATURAS:* ${dados.qtdViaturas}
*J. QUANTIDADE DE BOMBEIROS:* ${dados.qtdBombeiros}
*K. ENCARREGADO NO LOCAL DA OCORRÊNCIA:* ${encarregadoLocal}
*L. HISTÓRICO INICIAL:* ${dados.historicoInicial}
*M. HISTÓRICO FINAL:* ${dados.historicoFinal}
*N. NOME PM TRANSMISSÃO:* ${pmTransmissao}
*O. TEMPO PRIMEIRA VTR NO LOCAL:* ${dados.tempoVTR}
*P. OFICIAIS QUE COMPARECERAM NO LOCAL:* ${oficiaisLocal}
  `.trim();

  return output;
}

// ----------------------------------------------------------------------
// NOVAS FUNÇÕES PARA CARREGAMENTO E HIERARQUIA DE UNIDADES
// ----------------------------------------------------------------------

/**
 * Converte o número do SGB lido da planilha (ex: 1) para o formato de string 
 * esperado no HTML (ex: "1º SGB").
 */
function formatarSGB(sgbValue) {
  // Converte para string e remove espaços, caso o valor venha como número ou string
  const sgbStr = String(sgbValue).trim();
  
  // Se já for um formato 'Xº SGB', retorna como está
  if (sgbStr.includes('SGB')) {
    return sgbStr;
  }
  
  // Converte o número para o formato esperado: "Xº SGB"
  return sgbStr + 'º SGB';
}

/**
 * Lê os dados da Planilha Google, processa e constrói o objeto hierárquico GB -> SGB -> EB.
 * Usa o ID e o nome da aba fornecidos pelo usuário.
 * @returns {Object} O objeto de mapeamento de unidades.
 */
function getHierarquiaBombeiros() {
  // ID da planilha fornecida pelo usuário
  const ID_PLANILHA_DADOS = '1RrYuTW6iGUMRZHJ8X4bXvXENfa0MTuecAWqgri-xteU'; 
  // Nome da aba fornecida pelo usuário
  const NOME_ABA = 'est'; 
  
  let ss;
  try {
    ss = SpreadsheetApp.openById(ID_PLANILHA_DADOS);
  } catch (e) {
    Logger.log("Erro ao abrir a planilha. Verifique o ID. Erro: " + e.message);
    // Lança um erro que será capturado pelo onFailure no lado cliente
    throw new Error("Não foi possível acessar a planilha. ID incorreto ou permissão negada.");
  }
  
  const sheet = ss.getSheetByName(NOME_ABA);
  if (!sheet) {
    throw new Error(`A aba com o nome "${NOME_ABA}" não foi encontrada na planilha.`);
  }

  const lastRow = sheet.getLastRow();
  // Se houver menos de 2 linhas, consideramos apenas o cabeçalho
  if (lastRow < 2) { 
    Logger.log("Planilha vazia ou com apenas cabeçalho.");
    return {};
  }
  
  // Lê 3 colunas (GB, SGB, EB), começando da linha 2
  const range = sheet.getRange(2, 1, lastRow - 1, 3);
  const data = range.getValues();
  
  const hierarquia = {};

  data.forEach(row => {
    // Garante que todas as 3 colunas existam e não sejam nulas
    if (row[0] !== undefined && row[1] !== undefined && row[2] !== undefined) {
      const gb = String(row[0]).trim();     // Coluna 1 (A): GB
      const sgbNumero = String(row[1]).trim(); // Coluna 2 (B): SGB (apenas número)
      const eb = String(row[2]).trim();     // Coluna 3 (C): EB
      
      // Formata o SGB (ex: 1 -> 1º SGB)
      const sgb = formatarSGB(sgbNumero);
      
      if (gb && sgb && eb) {
        // 1. Cria o GB se não existir
        if (!hierarquia[gb]) {
          hierarquia[gb] = {};
        }
        
        // 2. Cria o SGB dentro do GB se não existir
        if (!hierarquia[gb][sgb]) {
          hierarquia[gb][sgb] = [];
        }
        
        // 3. Adiciona a EB ao SGB (usando a string formatada)
        if (!hierarquia[gb][sgb].includes(eb)) {
           hierarquia[gb][sgb].push(eb);
        }
      }
    }
  });

  return hierarquia;
}

/**
 * Ponto de entrada chamado pelo google.script.run do HTML.
 * @returns {Object} O objeto de hierarquia de unidades.
 */
function getUnidades() {
  return getHierarquiaBombeiros(); 
}