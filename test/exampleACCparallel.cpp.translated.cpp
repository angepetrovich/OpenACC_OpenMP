#include <iostream>
#include <stdlib.h>
#include <ctime>
using namespace std;

#define SIZE 15000
#define N (SIZE*SIZE)

void matrixAddition(const double A[], const double B[], double C[]) {

#pragma omp parallel for
	for (int x = 0; x < SIZE; x++) {
		for (int y = 0; y < SIZE; y++) {
			C[x*SIZE + y] = A[x*SIZE + y] + B[x*SIZE + y];
		}
	}
}

int main() {
    //deklaracja macierzy
    double* A = (double*)malloc(SIZE*SIZE* sizeof(double));
    double* B = (double*)malloc(SIZE*SIZE* sizeof(double));
    double* C = (double*)malloc(SIZE*SIZE* sizeof(double));
    clock_t begin, end;

   for(int x = 0; x <SIZE; x++){
       for(int y = 0; y <SIZE; y++){
            A[x*SIZE + y] = rand();
            B[x*SIZE + y] = rand();
        }
    }

    begin = clock();
    matrixAddition(A, B, C);
    end = clock();
    double elapsed = double(end - begin) / CLOCKS_PER_SEC;
    cout << "Czas wykonywania: " << elapsed << " [s]" << endl;

    free(A);
    free(B);
    free(C);

    return 0;

}