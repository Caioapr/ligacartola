// Função para buscar os dados da API e atualizar a tabela
function atualizarTabela() {
    fetch("/")
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('table-body');
            tableBody.innerHTML = ''; // Limpar o conteúdo atual da tabela

            // Iterar sobre os dados e criar as linhas da tabela
            data.forEach(pontuacao => {
                const newRow = `<tr>
                    <td>${pontuacao.rodada}</td>
                    <td>${pontuacao.id_time}</td>
                    <td>${pontuacao.pontos}</td>
                </tr>`;
                tableBody.insertAdjacentHTML('beforeend', newRow);
            });
        })
        .catch(error => console.error('Erro na solicitação:', error));
}

// Atualizar a tabela assim que a página for carregada
document.addEventListener('DOMContentLoaded', atualizarTabela);

// Atualizar a tabela a cada 10 segundos
setInterval(atualizarTabela, 12000000);
