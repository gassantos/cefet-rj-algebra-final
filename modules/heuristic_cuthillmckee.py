
"""
    Description
    -----------
    Solve a linear equation Ax = b with conjugate gradient method.
    Parameters
    ----------
    A: 2d numpy.array of positive semi-definite (symmetric) matrix
    b: 1d numpy.array
    x: 1d numpy.array of initial point
    Returns
    -------
    1d numpy.array x such that Ax = b
"""

# Coleção de matrizes esparsas: https://sparse.tamu.edu

import argparse
import numpy as np
import datetime as date
import time as time

from scipy.io.mmio import mmread
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee


# Definição do argumentos de execução
parser = argparse.ArgumentParser(description="Tempo de Execucao da Heuristica para Reducao de Largura de Banda")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true")
group.add_argument("-q", "--quiet", action="store_true")
parser.add_argument("symetric_mode", type=bool, help=": True (ou False), se a Matriz for simetrica (ou nao simetrica)")
parser.add_argument("filename", type=str, help=": O nome do arquivo da matriz (extensoes .mtx, .mtz.gz)")
args = parser.parse_args()

if args.quiet:
    print("Estao faltando argumentos")
elif args.verbose:
    print("A Reducao de Largura de Banda vai ser aplicada na Matriz (*.mtx) {} com forma SIMETRICA = {}.".format(args.filename, args.symetric_mode))


# Carregando o arquivo de formao Matriz Market filename
matriz = mmread(args.filename)
print("\nApresentando a Matriz:")
print("\tDimensao (M): ", matriz.shape)
print("\tElementos NONZERO: ", matriz.nnz)
print("\tArquivo da Matriz: ", args.filename)

# Convertendo com CSR uma Matriz Esparsa
G_sparse = csr_matrix(matriz)

print("\nAplicando a Heuristica REVERSE-CUTHIL-MCKEE")
t1 = time.time()
print("\tInicio\t- ", date.datetime.fromtimestamp(t1))
heuristica = reverse_cuthill_mckee(G_sparse, args.symetric_mode)
t2 = time.time()
print("\tTermino\t- ", date.datetime.fromtimestamp(t2))
print("Tempo de Execucao da Heuristica REVERSE-CUTHIL-MCKEE: ", t2 - t1)
print("\n")