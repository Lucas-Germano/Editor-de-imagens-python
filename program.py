import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Toplevel, ttk, colorchooser
import cv2
import numpy as np
from PIL import Image, ImageTk
import math
import matplotlib.pyplot as plt

class VisualizadorDeImagemInterativo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Projeto versão 4.2")
        self.root.state('zoomed')  

        # Estilo TTK
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('TLabel', font=('Courier', 10))

        # Frame principal
        self.frame_principal = ttk.Frame(self.root, padding=(10, 10, 10, 10))
        self.frame_principal.grid(row=0, column=0, sticky="nsew")

        # Canvas dentro do frame
        self.canvas_frame = ttk.Frame(self.frame_principal, borderwidth=2, relief="groove")
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, bg="#7f7f7f")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Configurar a grid do frame principal
        self.frame_principal.grid_rowconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

        # Cria o menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # Cria o submenu "Arquivo"
        self.submenu_arquivo = tk.Menu(self.menu)
        self.menu.add_cascade(label="Arquivo", menu=self.submenu_arquivo)
        self.submenu_arquivo.add_command(label="Abrir Imagem", command=self.abrir_imagem)
        self.submenu_arquivo.add_command(label="Salvar Imagem", command=self.salvar_imagem)

        # Cria o submenu "Editar"
        self.submenu_editar = tk.Menu(self.menu)
        self.menu.add_cascade(label="Editar", menu=self.submenu_editar)
        self.submenu_editar.add_command(label="Criar Negativo", command=self.criar_negativo)
        self.submenu_editar.add_command(label="Inverter Horizontalmente", command=self.inverter_horizontalmente)
        self.submenu_editar.add_command(label="Inverter Verticalmente", command=self.inverter_verticalmente)
        self.submenu_editar.add_command(label="Rotacionar Esquerda", command=self.rotacionar_esquerda)
        self.submenu_editar.add_command(label="Rotacionar Direita", command=self.rotacionar_direita)
        self.submenu_editar.add_command(label="Definir Escala", command=self.definir_escala)
        self.submenu_editar.add_command(label="Deslocar Para Direita", command=self.deslocar_direita)
        self.submenu_editar.add_command(label="Deslocar Para Esquerda", command=self.deslocar_esquerda)
        self.submenu_editar.add_command(label="Redimensionar Imagem", command=self.redimensionar_imagem)
        self.submenu_editar.add_command(label="Mudar cor de fundo", command=self.mudar_cor_fundo)

        # Cria o submenu filtros
        self.submenu_filtros = tk.Menu(self.menu)
        self.menu.add_cascade(label="Filtros", menu=self.submenu_filtros)
        self.submenu_filtros.add_command(label="Filtro de Desfoque", command=self.filtro_desfoque)
        self.submenu_filtros.add_command(label="Filtro de Bordas", command=self.filtro_bordas)
        self.submenu_filtros.add_command(label="Filtro de Escala de Cinza", command=self.filtro_cinza)
        self.submenu_filtros.add_command(label="Filtro Sepia", command=self.filtro_sepia)
        self.submenu_filtros.add_command(label="Filtro Azul", command=self.filtro_azul)
        self.submenu_filtros.add_command(label="Filtro Vermelho", command=self.filtro_vermelho)
        self.submenu_filtros.add_command(label="Filtro Verde", command=self.filtro_verde)
        self.submenu_filtros.add_command(label="Filtro Nitidez", command=self.filtro_nitidez)

        # Cria o submenu histograma
        self.submenu_histograma = tk.Menu(self.menu)
        self.menu.add_cascade(label="Histogramas", menu=self.submenu_histograma)
        self.submenu_histograma.add_command(label="Histograma Linha", command=self.histograma_linha)
        self.submenu_histograma.add_command(label="Histograma Coluna", command=self.histograma_coluna)
        self.submenu_histograma.add_command(label="Histograma Cinza linha", command=self.histograma_cinza_linha)
        self.submenu_histograma.add_command(label="Histograma Cinza coluna", command=self.histograma_cinza_coluna)

        # Cria o submenu "Recortar"
        self.menu.add_command(label="Recortar", command=self.recortar_imagem)

        # Cria o submenu "Matriz"
        self.menu.add_command(label="Gerar Matriz", command=self.criar_matriz)

        # Cria o submenu "Desfazer"
        self.menu.add_command(label="Desfazer", command=self.desfazer)

        # Cria o submenu "Refazer"
        self.menu.add_command(label="Refazer", command=self.refazer)

        # Cria o submenu "Mostrar Histórico"
        self.menu.add_command(label="Mostrar Histórico", command=self.mostrar_historico)

        # Adiciona uma barra de status
        self.status = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 5, 5, 5))
        self.status.grid(row=1, column=0, sticky="ew")

        # muda a fonte dos submenus
        fonte = ("Arial", 10)
        self.submenu_arquivo.configure(font=fonte)
        self.submenu_editar.configure(font=fonte)
        self.submenu_filtros.configure(font=fonte)
        self.submenu_histograma.configure(font=fonte)

        self.imagem_original = None
        self.imagem = None
        self.imagem_path = None
        self.imagem_criada = None

        self.recorte = None
        self.ref_point = []
        self.cropping = False

        # Fator de escala padrão
        self.escala = 0.9

        # Histórico para desfazer/refazer
        self.historico = []
        self.historico_indice = -1

        # Configurar a grid da janela principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def salvar_historico(self):
        if self.imagem_original:
            self.historico = self.historico[:self.historico_indice+1]
            self.historico.append(self.imagem_original.copy())
            self.historico_indice += 1

    def desfazer(self):
        if self.historico_indice > 0:
            self.historico_indice -= 1
            self.imagem_original = self.historico[self.historico_indice].copy()
            self.atualizar_imagem()

    def refazer(self):
        if self.historico_indice < len(self.historico) - 1:
            self.historico_indice += 1
            self.imagem_original = self.historico[self.historico_indice].copy()
            self.atualizar_imagem()
   
    def deslocar_direita(self):
        if self.imagem:
            amplitude = 50  # Amplitude do movimento
            periodo = 60  # Período do movimento (em frames)
            largura_imagem, _ = self.imagem_original.size
            for t in range(periodo):
                deslocamento = int(amplitude * math.sin(2 * math.pi * t / periodo))
                self.canvas.move(self.imagem_criada, deslocamento, 0)
                self.root.update()  # Atualiza a janela
                self.root.after(50)  # Aguarda 50 milissegundos antes de atualizar o próximo frame

    def deslocar_esquerda(self):
        if self.imagem:
            amplitude = 50  # Amplitude do movimento
            periodo = 60  # Período do movimento (em frames)
            largura_imagem, _ = self.imagem_original.size
            for t in range(periodo):
                deslocamento = int(amplitude * math.sin(2 * math.pi * t / periodo))
                self.canvas.move(self.imagem_criada, -deslocamento, 0)
                self.root.update()  # Atualiza a janela
                self.root.after(50)  # Aguarda 50 milissegundos antes de atualizar o próximo frame

    def abrir_imagem(self):
        self.imagem_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if self.imagem_path:
            self.carregar_imagem(self.imagem_path)
            self.status.config(text="Imagem aberta: " + self.imagem_path)

    def carregar_imagem(self, caminho_imagem):
        imagem_original = cv2.imread(caminho_imagem)
        imagem_original = cv2.cvtColor(imagem_original, cv2.COLOR_BGR2RGB)
        self.imagem_original = Image.fromarray(imagem_original)
        self.atualizar_imagem()

    def atualizar_imagem(self):
        largura_canvas = self.canvas.winfo_width()
        altura_canvas = self.canvas.winfo_height()

        largura_imagem = int(self.imagem_original.width * self.escala)
        altura_imagem = int(self.imagem_original.height * self.escala)

        x = (largura_canvas - largura_imagem) // 2
        y = (altura_canvas - altura_imagem) // 2

        self.imagem = ImageTk.PhotoImage(self.imagem_original.resize((largura_imagem, altura_imagem)))
        self.canvas.config(width=largura_canvas, height=altura_canvas)
        self.imagem_criada = self.canvas.create_image(x, y, anchor=tk.NW, image=self.imagem)

    def selecionar_area(self, event):
        if self.cropping:
            if len(self.ref_point) == 1:
                self.ref_point.append((event.x, event.y))
            else:
                self.ref_point[1] = (event.x, event.y)
            self.canvas.delete("rect")
            self.canvas.create_rectangle(self.ref_point[0][0], self.ref_point[0][1], event.x, event.y, outline="green", tag="rect")
        else:
            self.ref_point = [(event.x, event.y)]
            self.cropping = True

    def finalizar_selecao(self, event):
        if self.cropping:
            if len(self.ref_point) == 1:
                self.ref_point.append((event.x, event.y))
            else:
                self.ref_point[1] = (event.x, event.y)
        self.cropping = False
        self.canvas.delete("rect")
        self.recortar_area()
        # Remover os bindings dos eventos de mouse
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def recortar_area(self):
        if len(self.ref_point) == 2:
            x0, y0 = self.ref_point[0]
            x1, y1 = self.ref_point[1]

            # Ajustar coordenadas para estarem dentro da imagem
            largura_canvas = self.canvas.winfo_width()
            altura_canvas = self.canvas.winfo_height()

            largura_imagem = int(self.imagem_original.width * self.escala)
            altura_imagem = int(self.imagem_original.height * self.escala)

            x_offset = (largura_canvas - largura_imagem) // 2
            y_offset = (altura_canvas - altura_imagem) // 2

            x0 = max(x0 - x_offset, 0)
            y0 = max(y0 - y_offset, 0)
            x1 = min(x1 - x_offset, largura_imagem)
            y1 = min(y1 - y_offset, altura_imagem)

            # Ajustar as coordenadas de volta para a escala original
            x0 = int(x0 / self.escala)
            y0 = int(y0 / self.escala)
            x1 = int(x1 / self.escala)
            y1 = int(y1 / self.escala)

            if x0 < x1 and y0 < y1:
                self.salvar_historico()
                self.imagem_original = self.imagem_original.crop((x0, y0, x1, y1))
                self.atualizar_imagem()
                self.ref_point = []  # Reinicializa os pontos de referência


    def recortar_imagem(self):
        self.status.config(text="Clique e arraste para selecionar a área de recorte.")
        self.canvas.bind("<ButtonPress-1>", self.selecionar_area)
        self.canvas.bind("<B1-Motion>", self.selecionar_area)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_selecao)
        
    def mudar_cor_fundo(self):
        cor_fundo = colorchooser.askcolor(title="Escolha a cor de fundo")
        if cor_fundo:
            self.canvas.config(bg=cor_fundo[1])

    def redimensionar_imagem(self):
        if self.imagem_original:
            nova_largura = simpledialog.askinteger("Redimensionar Imagem", "Digite a nova largura:")
            nova_altura = simpledialog.askinteger("Redimensionar Imagem", "Digite a nova altura:")
            if nova_largura and nova_altura:
                self.salvar_historico()
                self.imagem_original = self.imagem_original.resize((nova_largura, nova_altura))
                self.atualizar_imagem()
                self.status.config(text=f"Imagem redimensionada para {nova_largura}x{nova_altura}")


    def criar_negativo(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_negativa = cv2.bitwise_not(np.array(self.imagem_original))
            self.imagem_original = Image.fromarray(imagem_negativa)
            self.atualizar_imagem()

    def inverter_horizontalmente(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_invertida = cv2.flip(np.array(self.imagem_original), 1)
            self.imagem_original = Image.fromarray(imagem_invertida)
            self.atualizar_imagem()

    def inverter_verticalmente(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_invertida = cv2.flip(np.array(self.imagem_original), 0)
            self.imagem_original = Image.fromarray(imagem_invertida)
            self.atualizar_imagem()

    def rotacionar_esquerda(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_rotacionada = np.rot90(np.array(self.imagem_original))
            self.imagem_original = Image.fromarray(imagem_rotacionada)
            self.atualizar_imagem()

    def rotacionar_direita(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_rotacionada = np.rot90(np.array(self.imagem_original), 3)
            self.imagem_original = Image.fromarray(imagem_rotacionada)
            self.atualizar_imagem()

    def definir_escala(self):
        escala = simpledialog.askfloat("Definir Escala", "Digite a escala (porcentagem):", initialvalue=self.escala)
        if escala is not None:
            self.salvar_historico()
            self.escala = escala / 100
            self.atualizar_imagem()
            self.status.config(text=f"Escala definida para {self.escala * 100}%")

    def salvar_imagem(self):
        if self.imagem_original:
            caminho_salvar = filedialog.asksaveasfilename(defaultextension=".png",
                                                           filetypes=[("Imagem PNG", "*.png"), ("Todos os arquivos", "*.*")])
            if caminho_salvar:
                self.imagem_original.save(caminho_salvar)
                self.status.config(text="Imagem salva como: " + caminho_salvar)

    def criar_matriz(self):
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja gerar a matriz?")
        if resposta:
            if self.imagem_original is not None:
                matriz = np.array(self.imagem_original)
                self.mostrar_matriz(matriz)

    def mostrar_matriz(self, matriz):
        nova_janela = tk.Toplevel(self.root)
        nova_janela.title("Matriz da Imagem")

        # Criação do widget Text e Scrollbar
        texto_matriz = tk.Text(nova_janela, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(nova_janela, orient=tk.VERTICAL, command=texto_matriz.yview)
        texto_matriz.config(yscrollcommand=scrollbar.set)

        # Posicionamento dos widgets na janela
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        texto_matriz.pack(expand=True, fill=tk.BOTH)

        # Construindo a representação textual da matriz
        altura, largura, _ = matriz.shape
        for y in range(altura):
            linha_texto = ""
            for x in range(largura):
                coordenada = f"({y}, {x})"
                cor = matriz[y][x]
                linha_texto += f"{coordenada}: {cor};\t"
            texto_matriz.insert(tk.END, linha_texto + "\n")

    def mostrar_historico(self):
        if not self.historico:
            messagebox.showinfo("Histórico Vazio", "Não há alterações no histórico.")
            return

        nova_janela = Toplevel(self.root)
        nova_janela.title("Histórico de Alterações")
        nova_janela.state('zoomed')  # Abre a janela maximizada

        frame_historico = ttk.Frame(nova_janela, padding="10")
        frame_historico.grid(row=0, column=0, sticky="nsew")

        # Configura a expansão do frame_historico
        nova_janela.grid_rowconfigure(0, weight=1)
        nova_janela.grid_columnconfigure(0, weight=1)

        canvas_historico = tk.Canvas(frame_historico, bg="#ffffff")
        canvas_historico.grid(row=0, column=0, sticky="nsew")

        # Configura a expansão do canvas_historico
        frame_historico.grid_rowconfigure(0, weight=1)
        frame_historico.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(frame_historico, orient=tk.VERTICAL, command=canvas_historico.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        canvas_historico.config(yscrollcommand=scrollbar.set)

        frame_miniaturas = ttk.Frame(canvas_historico)
        canvas_historico.create_window((0, 0), window=frame_miniaturas, anchor="nw")

        def on_canvas_configure(event):
            canvas_historico.config(scrollregion=canvas_historico.bbox("all"))

        canvas_historico.bind("<Configure>", on_canvas_configure)

        miniaturas_por_linha = 4  # Defina quantas miniaturas você quer por linha

        for i, imagem in enumerate(self.historico):
            miniatura = ImageTk.PhotoImage(imagem.resize((457, 300)))
            label_miniatura = tk.Label(frame_miniaturas, image=miniatura)
            label_miniatura.image = miniatura  # Para manter uma referência e evitar coleta de lixo
            label_miniatura.grid(row=i // miniaturas_por_linha, column=i % miniaturas_por_linha, padx=5, pady=5)

            def selecionar_imagem(indice=i):
                self.imagem_original = self.historico[indice].copy()
                self.historico_indice = indice
                self.atualizar_imagem()
                nova_janela.destroy()

            label_miniatura.bind("<Button-1>", lambda e, indice=i: selecionar_imagem(indice))

        # Atualiza a área de rolagem do canvas
        frame_miniaturas.update_idletasks()
        canvas_historico.config(scrollregion=canvas_historico.bbox("all"))


    def histograma_coluna(self):
        if self.imagem_original is not None:
            imagem_np = np.array(self.imagem_original)
            cores = ('r', 'g', 'b')
            plt.figure()
            
            for i, cor in enumerate(cores):
                histograma = cv2.calcHist([imagem_np], [i], None, [256], [0, 256])
                plt.bar(range(256), histograma.flatten(), color=cor, alpha=0.5)
            
            plt.title('Histograma')
            plt.xlabel('Intensidade')
            plt.ylabel('Frequência')
            plt.xlim([0, 256])
            plt.ylim([0, max(histograma.flatten())])
            plt.show()

    def histograma_linha(self):
        if self.imagem_original is not None:
            imagem_np = np.array(self.imagem_original)
            cores = ('r', 'g', 'b')
            plt.figure()
            
            for i, cor in enumerate(cores):
                histograma = cv2.calcHist([imagem_np], [i], None, [256], [0, 256])
                plt.plot(histograma, color=cor)
            
            plt.title('Histograma')
            plt.xlabel('Intensidade')
            plt.ylabel('Frequência')
            plt.xlim([0, 256])
            plt.ylim([0, max(histograma.flatten())])
            plt.show()

    def histograma_cinza_linha(self):
        if self.imagem_original is not None:
            imagem_np = np.array(self.imagem_original)
            imagem_cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2GRAY)
            histograma = cv2.calcHist([imagem_cinza], [0], None, [256], [0, 256])
            
            plt.figure()
            plt.title("Histograma de Cinza")
            plt.xlabel("Intensidade")
            plt.ylabel("Frequência")
            plt.plot(histograma, color="gray")
            plt.xlim([0, 256])
            plt.ylim([0, max(histograma.flatten())])
            plt.show()

    def histograma_cinza_coluna(self):
        if self.imagem_original is not None:
            imagem_np = np.array(self.imagem_original)
            imagem_cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2GRAY)
            histograma = cv2.calcHist([imagem_cinza], [0], None, [256], [0, 256])
            
            plt.figure()
            plt.title("Histograma de Cinza")
            plt.xlabel("Intensidade")
            plt.ylabel("Frequência")
            plt.bar(range(256), histograma.flatten(), color='gray', width=1.0)
            plt.xlim([0, 256])
            plt.ylim([0, max(histograma.flatten())])
            plt.show()

    def filtro_desfoque(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_desfocada = cv2.GaussianBlur(imagem_np, (15, 15), 0)
            self.imagem_original = Image.fromarray(imagem_desfocada)
            self.atualizar_imagem()

    def filtro_bordas(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2GRAY)
            imagem_bordas = cv2.Canny(imagem_cinza, 100, 200)
            imagem_bordas_rgb = cv2.cvtColor(imagem_bordas, cv2.COLOR_GRAY2RGB)
            self.imagem_original = Image.fromarray(imagem_bordas_rgb)
            self.atualizar_imagem()

    def filtro_nitidez(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            imagem_nitida = cv2.filter2D(imagem_np, -1, kernel)
            self.imagem_original = Image.fromarray(imagem_nitida)
            self.atualizar_imagem()

    def filtro_cinza(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGB2GRAY)
            imagem_cinza_rgb = cv2.cvtColor(imagem_cinza, cv2.COLOR_GRAY2RGB)
            self.imagem_original = Image.fromarray(imagem_cinza_rgb)
            self.atualizar_imagem()

    def filtro_sepia(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_sepia = np.array(imagem_np, dtype=np.float64)
            imagem_sepia = cv2.transform(imagem_sepia, np.matrix([[0.393, 0.769, 0.189],
                                                                  [0.349, 0.686, 0.168],
                                                                  [0.272, 0.534, 0.131]]))
            imagem_sepia[np.where(imagem_sepia > 255)] = 255
            imagem_sepia = np.array(imagem_sepia, dtype=np.uint8)
            self.imagem_original = Image.fromarray(imagem_sepia)
            self.atualizar_imagem()

    def filtro_azul(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_azul = np.zeros_like(imagem_np)
            imagem_azul[:, :, 2] = imagem_np[:, :, 2]  # Preserva o canal azul
            self.imagem_original = Image.fromarray(imagem_azul)
            self.atualizar_imagem()

    def filtro_vermelho(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_vermelho = np.zeros_like(imagem_np)
            imagem_vermelho[:, :, 0] = imagem_np[:, :, 0]  # Preserva o canal vermelho
            self.imagem_original = Image.fromarray(imagem_vermelho)
            self.atualizar_imagem()

    def filtro_verde(self):
        if self.imagem_original:
            self.salvar_historico()
            imagem_np = np.array(self.imagem_original)
            imagem_verde = np.zeros_like(imagem_np)
            imagem_verde[:, :, 1] = imagem_np[:, :, 1]  # Preserva o canal verde
            self.imagem_original = Image.fromarray(imagem_verde)
            self.atualizar_imagem()

    def iniciar(self):
        self.root.mainloop()

# Exemplo de uso:
visualizador = VisualizadorDeImagemInterativo()
visualizador.iniciar()
