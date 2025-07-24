#include <unistd.h>
#include <stdlib.h>
#include <time.h>

#define IO_JTAG_UART (*(volatile unsigned int *)0xFF201000)
#define VGA_BASE 0xc8000000
uint16_t *ppix = (uint16_t *)(VGA_BASE);

#define BOTOES_BASE 0xFF200050
uint8_t *pointer_botoes = (uint8_t *)(BOTOES_BASE);

#define BLUE 0x001F
#define RED 0xF800
#define GREEN 0x07E0
#define BLACK 0x0000
#define WHITE 0xFFFF
#define GRAY 0x8410
#define MAGENTA 0xF81F
#define YELLOW 0xFFE0
#define CYAN 0x07FF

#define BOTAO_0 0x01
#define BOTAO_1 0x02
#define BOTAO_2 0x04
#define BOTAO_3 0x08

#define TAMANHO_MUNDO_X 320
#define TAMANHO_MUNDO_Y 240

uint16_t SpritePlayer1[16 * 12]= {
    BLACK, BLACK, BLACK, BLACK, YELLOW, YELLOW, YELLOW, YELLOW, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK, BLACK, BLACK,
    BLACK, BLACK, YELLOW, YELLOW, BLACK, YELLOW, YELLOW, BLACK, YELLOW, YELLOW, BLACK, BLACK,
    BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK,
    BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK,
    BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK,
    BLACK, BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK, BLACK,
    BLACK, BLACK, BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, BLACK, YELLOW, YELLOW, YELLOW, YELLOW, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, YELLOW, YELLOW, BLACK, BLACK, YELLOW, YELLOW, BLACK, BLACK, BLACK,
    BLACK, BLACK, YELLOW, YELLOW, BLACK, BLACK, BLACK, BLACK, YELLOW, YELLOW, BLACK, BLACK,
    BLACK, YELLOW, YELLOW, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, YELLOW, YELLOW, BLACK,
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK,
    BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK
};

uint16_t TELA[TAMANHO_MUNDO_X * TAMANHO_MUNDO_Y];

int botaoApertado(int num_botao) {
    return *pointer_botoes & num_botao;
}

void escreveTela(){
    for(int i=0; i < TAMANHO_MUNDO_X; i++){
        for(int j=0; j < TAMANHO_MUNDO_Y; j++){
            ppix[i + (j*512)] = TELA[i + (j*TAMANHO_MUNDO_X)];
        }
    }
}

void delay() {
    volatile int count = 0;
    for (count = 0; count < 1000000; count++) {}
}

void setPix(int lin, int col, uint16_t cor){
	if( lin<0 || lin>TAMANHO_MUNDO_X){
		return;
	}
	if(col<0 || col>TAMANHO_MUNDO_Y){
		return;
	}
	TELA[lin + (col*TAMANHO_MUNDO_X )] = cor;
}

void tile (int x0, int y0, int x1, int y1, uint16_t cor){ 
	if (x0 > x1){ int aux = x0; x0 = x1; x1 = aux; }
	if (y0 > y1){ int aux = y0; y0 = y1; y1 = aux; }
	for(int i = x0; i < x1; i++){
		for(int j = y0; j < y1; j++){
			setPix(i,j,cor);
		}
	}
}

void fundo (uint16_t cor){
	tile(0,0,TAMANHO_MUNDO_X,TAMANHO_MUNDO_Y,cor);
}

typedef struct Entidade {
    int posicaoX;
    int posicaoY;
    int velX;
    int velY;
    uint16_t *sprite;
    int tamanhoSpriteX;
    int tamanhoSpriteY;
}Entidade;

void desenharEntidade(Entidade* entidade){
    if(entidade->sprite == NULL){
        tile(entidade->posicaoX-5, entidade->posicaoY-5, entidade->posicaoX + 5, entidade->posicaoY + 5, RED);
        return;
    }
    
    // Desenha sprite
    for(int i=0; i < entidade->tamanhoSpriteX; i++){
        for(int j=0; j < entidade->tamanhoSpriteY; j++){
            setPix( entidade->posicaoX+i, entidade->posicaoY+j, entidade->sprite[i + (j*entidade->tamanhoSpriteX)]);
        }
    }

}

void processPlayerInput(Entidade* entidade){
    int direcaoX = 0;
    int direcaoY = 0;
    if(botaoApertado(BOTAO_0)){
        direcaoX += 1;
    }
    if(botaoApertado(BOTAO_1)){
        direcaoY += -1;
    }
    if(botaoApertado(BOTAO_2)){
        direcaoY += 1;
    }
    if(botaoApertado(BOTAO_3)){
        direcaoX += -1;
    }
    entidade->velX = direcaoX;
    entidade->velY = direcaoY;
}

void processaFisicaEntidade(Entidade* entidade){
    entidade->posicaoX += entidade->velX;
    entidade->posicaoY += entidade->velY;
}

typedef struct Mapa{
    // Lista de entidades;
    Entidade entidades[10];
    Entidade player;
} Mapa;

void desenharEntidades(Entidade* entidades, int quantidadeEntidades){
    for(int i=0;i<quantidadeEntidades;i++){
        desenharEntidade(&entidades[i]);
    }
}

// Objetivo atual: Adicionar mais entidades no mundo
// Ter quantidade dinamica de entidades na tela (1, 5, 0)
// Desenhar entidades diferentes
int main(){
    srand(time(NULL));

    Mapa mundo;
    mundo.player.posicaoX = 160;
    mundo.player.posicaoY = 120;
    mundo.player.sprite = (uint16_t*)SpritePlayer1;
    mundo.player.tamanhoSpriteX = 16;
    mundo.player.tamanhoSpriteY = 12;

    // Inicializa entidades
    for(int i=0;i<10;i++){
        mundo.entidades[i].sprite = NULL;
        mundo.entidades[i].posicaoX = rand() % TAMANHO_MUNDO_X;
        mundo.entidades[i].posicaoY = rand() % TAMANHO_MUNDO_Y;
    }
    
    while(1){
        fundo(WHITE);
        processPlayerInput(&mundo.player);
        processaFisicaEntidade(&mundo.player);

        // // Desenhos
        desenharEntidades(mundo.entidades, 10);
        desenharEntidade(&mundo.player);
        
        
        escreveTela();
    }

    return 0;
}