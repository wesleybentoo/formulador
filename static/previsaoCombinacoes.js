// Função auxiliar para calcular fatorial
function factorial(n) {
  let res = 1;
  for (let i = 2; i <= n; i++) {
    res *= i;
  }
  return res;
}

// Função auxiliar para calcular combinação: C(a, b) = a! / (b!(a-b)!)
function combinacao(a, b) {
  return factorial(a) / (factorial(b) * factorial(a - b));
}

// Calcula o número de maneiras de distribuir 100% (em unidades definidas pelo step)
// entre "numMaterias" matérias-primas.
function combinarPossibilidades(numMaterias, step) {
  const n = 100 / step;  // número total de unidades (ex: 10 para step = 10)
  // Número de soluções não–negativas para x1 + ... + xL = n
  // É dado por: C(n + L - 1, L - 1)
  return combinacao(n + numMaterias - 1, numMaterias - 1);
}

function preverTotalCombinacoes(formulado, materiasPrimas, step = 10) {
  // Extrai os valores do formulado (N-P-K)
  const [targetN, targetP, targetK] = formulado.split('-').map(parseFloat);

  // Define quais nutrientes são exigidos (se o valor for maior que zero)
  const nutrientesRelevantes = {
    N: targetN > 0,
    P: targetP > 0,
    K: targetK > 0
  };

  // Filtra as matérias-primas que realmente fornecem o nutriente desejado
  const materiasPorNutriente = {
    N: materiasPrimas.filter(mp =>
      nutrientesRelevantes.N &&
      mp.nutrients.some(n => n.name === 'N' && parseFloat(n.percent) > 0)
    ),
    P: materiasPrimas.filter(mp =>
      nutrientesRelevantes.P &&
      mp.nutrients.some(n => n.name.startsWith('P') && parseFloat(n.percent) > 0)
    ),
    K: materiasPrimas.filter(mp =>
      nutrientesRelevantes.K &&
      mp.nutrients.some(n => n.name.startsWith('K') && parseFloat(n.percent) > 0)
    )
  };

  // Calcula as possibilidades para cada nutriente usando a fórmula de estrelas e barras
  const possibilidadesPorNutriente = {};
  for (const nutr of ['N', 'P', 'K']) {
    if (!nutrientesRelevantes[nutr] || materiasPorNutriente[nutr].length === 0) {
      possibilidadesPorNutriente[nutr] = 1;
    } else {
      possibilidadesPorNutriente[nutr] = combinarPossibilidades(materiasPorNutriente[nutr].length, step);
    }
  }

  // O total de combinações é o produto das combinações para cada nutriente exigido
  const totalCombinacoes = possibilidadesPorNutriente['N'] *
                           possibilidadesPorNutriente['P'] *
                           possibilidadesPorNutriente['K'];

  return totalCombinacoes;
}

