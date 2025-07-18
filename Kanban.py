import customtkinter as ctk
import tkinter as tk # Necessário para algumas constantes como tk.END
from tkinter import messagebox # Usar messagebox do tkinter padrão
import json
import os
import uuid

# Nome do ficheiro para persistência dos dados
ARQUIVO_TAREFAS = "kanban_data_ctk.json" 
# Status possíveis para as tarefas (e nomes das colunas)
STATUS_COLUNAS = ["A Fazer", "Em Andamento", "Concluído"]
# Categorias possíveis para as tarefas
CATEGORIAS_TAREFAS = ["Trabalho", "Pessoal", "Faculdade", "Outro"] 
# Lista global para armazenar as tarefas em memória
tarefas_data = []

# Aparência e tema do CustomTkinter
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme("blue") 

# --- Lógica de Dados ---
def carregar_tarefas_data():
    """Carrega as tarefas do ficheiro JSON."""
    global tarefas_data
    if os.path.exists(ARQUIVO_TAREFAS):
        try:
            with open(ARQUIVO_TAREFAS, 'r', encoding='utf-8') as f:
                tarefas_data = json.load(f)
                # Garantir que tarefas antigas tenham um campo de categoria (opcional, mas bom para consistência)
                for tarefa in tarefas_data:
                    if "categoria" not in tarefa:
                        tarefa["categoria"] = "Outro" 
        except json.JSONDecodeError:
            tarefas_data = []
            messagebox.showwarning("Atenção", f"O ficheiro {ARQUIVO_TAREFAS} está corrompido. A iniciar com lista de tarefas vazia.")
        except Exception as e:
            tarefas_data = []
            messagebox.showerror("Erro", f"Erro ao carregar tarefas: {e}. A iniciar com lista de tarefas vazia.")
    else:
        tarefas_data = []

def salvar_tarefas_data():
    """Salva a lista de tarefas atual no ficheiro JSON."""
    try:
        with open(ARQUIVO_TAREFAS, 'w', encoding='utf-8') as f:
            json.dump(tarefas_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar tarefas: {e}")

def gerar_id_unico():
    """Gera um ID único para uma nova tarefa."""
    return str(uuid.uuid4())

def encontrar_tarefa_por_id(id_tarefa):
    """Encontra uma tarefa na lista tarefas_data pelo seu ID."""
    for tarefa in tarefas_data:
        if tarefa['id'] == id_tarefa:
            return tarefa
    return None

# --- Componentes da UI ---

class DialogoTarefa(ctk.CTkToplevel):
    """Diálogo para adicionar ou editar uma tarefa."""
    def __init__(self, parent, app_ref, tarefa_existente=None):
        super().__init__(parent)
        self.app_ref = app_ref
        self.tarefa_existente = tarefa_existente

        categoria_inicial = CATEGORIAS_TAREFAS[0] 

        if self.tarefa_existente:
            self.title("Editar Tarefa")
            titulo_inicial = self.tarefa_existente["titulo"]
            descricao_inicial = self.tarefa_existente["descricao"]
            categoria_inicial = self.tarefa_existente.get("categoria", CATEGORIAS_TAREFAS[0])
        else:
            self.title("Nova Tarefa")
            titulo_inicial = ""
            descricao_inicial = ""

        self.geometry("400x380") 
        self.transient(parent) 
        self.grab_set() 

        self.label_titulo = ctk.CTkLabel(self, text="Título*:")
        self.label_titulo.pack(pady=(10,0), padx=20, anchor="w")
        self.entry_titulo = ctk.CTkEntry(self, width=360, placeholder_text="Título da tarefa")
        self.entry_titulo.pack(pady=(2,5), padx=20, fill="x")
        self.entry_titulo.insert(0, titulo_inicial)

        self.label_descricao = ctk.CTkLabel(self, text="Descrição:")
        self.label_descricao.pack(pady=(5,0), padx=20, anchor="w")
        self.textbox_descricao = ctk.CTkTextbox(self, width=360, height=100)
        self.textbox_descricao.pack(pady=(2,5), padx=20, fill="x")
        self.textbox_descricao.insert("1.0", descricao_inicial)

        self.label_categoria = ctk.CTkLabel(self, text="Categoria:")
        self.label_categoria.pack(pady=(5,0), padx=20, anchor="w")
        self.combobox_categoria = ctk.CTkComboBox(self, width=360, values=CATEGORIAS_TAREFAS)
        self.combobox_categoria.set(categoria_inicial)
        self.combobox_categoria.pack(pady=(2,10), padx=20, fill="x")


        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=20, padx=20, fill="x")

        self.botao_salvar = ctk.CTkButton(self.frame_botoes, text="Salvar", command=self.salvar)
        self.botao_salvar.pack(side="right", padx=(10,0))
        
        self.botao_cancelar = ctk.CTkButton(self.frame_botoes, text="Cancelar", command=self.destroy, fg_color="gray")
        self.botao_cancelar.pack(side="right")
        
        self.entry_titulo.focus() 

    def salvar(self):
        titulo = self.entry_titulo.get().strip()
        descricao = self.textbox_descricao.get("1.0", tk.END).strip()
        categoria = self.combobox_categoria.get()

        if not titulo:
            messagebox.showwarning("Campo Obrigatório", "O título da tarefa não pode ser vazio.", parent=self)
            self.entry_titulo.focus()
            return
        
        if not categoria or categoria not in CATEGORIAS_TAREFAS:
             messagebox.showwarning("Seleção Inválida", "Por favor, selecione uma categoria válida.", parent=self)
             return


        if self.tarefa_existente:
            self.tarefa_existente["titulo"] = titulo
            self.tarefa_existente["descricao"] = descricao
            self.tarefa_existente["categoria"] = categoria
            messagebox.showinfo("Sucesso", f"Tarefa '{titulo}' atualizada.", parent=self.master) 
        else:
            nova_tarefa = {
                "id": gerar_id_unico(),
                "titulo": titulo,
                "descricao": descricao,
                "categoria": categoria,
                "status": STATUS_COLUNAS[0]  
            }
            tarefas_data.append(nova_tarefa)
            messagebox.showinfo("Sucesso", f"Tarefa '{titulo}' adicionada.", parent=self.master)
        
        salvar_tarefas_data()
        self.app_ref.atualizar_quadro_kanban_ui()
        self.destroy()


class FrameTarefa(ctk.CTkFrame):
    """Frame para exibir uma tarefa individual."""
    def __init__(self, parent, tarefa_info, app_ref, coluna_origem_ref):
        super().__init__(parent, corner_radius=10, border_width=1)
        self.tarefa_info = tarefa_info
        self.app_ref = app_ref
        self.coluna_origem_ref = coluna_origem_ref

        self.configure(height=150) 

        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.pack(pady=(5,2), padx=10, fill="x", expand=False)

        self.label_titulo = ctk.CTkLabel(frame_conteudo, text=self.tarefa_info["titulo"], font=ctk.CTkFont(weight="bold", size=14), anchor="w", wraplength=180) 
        self.label_titulo.pack(fill="x")

        desc_curta = self.tarefa_info["descricao"]
        if len(desc_curta) > 50: 
            desc_curta = desc_curta[:47] + "..."
        
        self.label_descricao = ctk.CTkLabel(frame_conteudo, text=desc_curta if desc_curta else "Sem descrição", anchor="w", font=ctk.CTkFont(size=11), wraplength=180) 
        self.label_descricao.pack(fill="x")
        
        categoria_texto = self.tarefa_info.get("categoria", "N/A") 
        self.label_categoria_tarefa = ctk.CTkLabel(frame_conteudo, text=f"Cat: {categoria_texto}", font=ctk.CTkFont(size=10, slant="italic"), anchor="w", text_color=("gray50", "gray60"))
        self.label_categoria_tarefa.pack(fill="x", pady=(2,0))


        frame_botoes_tarefa = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes_tarefa.pack(pady=(0,5), padx=5, fill="x", side="bottom")

        index_status_atual = STATUS_COLUNAS.index(self.tarefa_info["status"])
        
        btn_mover_esquerda_estado = "normal" if index_status_atual > 0 else "disabled"
        self.btn_mover_esquerda = ctk.CTkButton(frame_botoes_tarefa, text="<", width=30, command=lambda: self.app_ref.mover_tarefa_logica(self.tarefa_info, -1), state=btn_mover_esquerda_estado)
        self.btn_mover_esquerda.pack(side="left", padx=(0,2))
        
        btn_mover_direita_estado = "normal" if index_status_atual < len(STATUS_COLUNAS) - 1 else "disabled"
        self.btn_mover_direita = ctk.CTkButton(frame_botoes_tarefa, text=">", width=30, command=lambda: self.app_ref.mover_tarefa_logica(self.tarefa_info, 1), state=btn_mover_direita_estado)
        self.btn_mover_direita.pack(side="left", padx=2)

        self.btn_excluir = ctk.CTkButton(frame_botoes_tarefa, text="Excluir", width=60, command=self.excluir_tarefa, fg_color="red", hover_color="#C62828")
        self.btn_excluir.pack(side="right", padx=2)
        
        self.btn_editar = ctk.CTkButton(frame_botoes_tarefa, text="Editar", width=60, command=self.editar_tarefa)
        self.btn_editar.pack(side="right", padx=(0,2))

    def editar_tarefa(self):
        DialogoTarefa(self.master.master.master, self.app_ref, tarefa_existente=self.tarefa_info) 

    def excluir_tarefa(self):
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a tarefa '{self.tarefa_info['titulo']}'?", parent=self.master.master.master):
            tarefas_data.remove(self.tarefa_info)
            salvar_tarefas_data()
            self.app_ref.atualizar_quadro_kanban_ui()
            messagebox.showinfo("Sucesso", "Tarefa excluída.", parent=self.master.master.master)

class ColunaKanban(ctk.CTkScrollableFrame):
    """Frame com scroll para uma coluna (status) do Kanban."""
    def __init__(self, parent, titulo_status, app_ref):
        super().__init__(parent, corner_radius=10, border_width=2)
        self.titulo_status = titulo_status
        self.app_ref = app_ref
        
        self.label_titulo_coluna = ctk.CTkLabel(self, text=self.titulo_status, font=ctk.CTkFont(size=18, weight="bold"))
        self.label_titulo_coluna.pack(pady=10, padx=10, fill="x")
        
        self.frame_interno_tarefas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_interno_tarefas.pack(fill="both", expand=True, padx=5, pady=5)

    def adicionar_tarefa_ui(self, tarefa_info):
        """Adiciona um FrameTarefa a esta coluna."""
        frame_tarefa = FrameTarefa(self.frame_interno_tarefas, tarefa_info, self.app_ref, self)
        frame_tarefa.pack(pady=5, padx=5, fill="x", anchor="n")

    def limpar_tarefas_ui(self):
        """Remove todos os frames de tarefa desta coluna."""
        for widget in self.frame_interno_tarefas.winfo_children():
            widget.destroy()


class KanbanApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quadro Kanban com CustomTkinter")
        self.geometry("1100x750")

        carregar_tarefas_data()

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame para os controles de topo (Adicionar, Pesquisa, Filtro)
        self.frame_controles_topo = ctk.CTkFrame(self.main_frame)
        self.frame_controles_topo.pack(pady=(0,10), fill="x")

        self.botao_adicionar_tarefa = ctk.CTkButton(self.frame_controles_topo, text="Adicionar Nova Tarefa", command=self.abrir_dialogo_nova_tarefa, height=40, font=ctk.CTkFont(size=14))
        self.botao_adicionar_tarefa.pack(side="left", padx=10, pady=10)
        
        self.entry_pesquisa = ctk.CTkEntry(self.frame_controles_topo, placeholder_text="Pesquisar...", width=200)
        self.entry_pesquisa.pack(side="left", padx=5, pady=10)
        self.entry_pesquisa.bind("<KeyRelease>", lambda event: self.atualizar_quadro_kanban_ui()) # Atualiza ao digitar

        categorias_filtro = ["Todas"] + CATEGORIAS_TAREFAS
        self.combobox_filtro_categoria = ctk.CTkComboBox(self.frame_controles_topo, values=categorias_filtro, command=lambda choice: self.atualizar_quadro_kanban_ui(), width=150)
        self.combobox_filtro_categoria.set("Todas")
        self.combobox_filtro_categoria.pack(side="left", padx=5, pady=10)

        self.botao_limpar_filtros = ctk.CTkButton(self.frame_controles_topo, text="Limpar", command=self.limpar_filtros_pesquisa, width=80)
        self.botao_limpar_filtros.pack(side="left", padx=5, pady=10)
        
        self.switch_tema = ctk.CTkSwitch(self.frame_controles_topo, text="Tema Escuro", command=self.mudar_tema)
        self.switch_tema.pack(side="right", padx=10, pady=10)
        if ctk.get_appearance_mode() == "Dark":
            self.switch_tema.select()

        self.frame_colunas = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.frame_colunas.pack(fill="both", expand=True)

        self.colunas_ui = {}
        for i, status in enumerate(STATUS_COLUNAS):
            self.frame_colunas.grid_columnconfigure(i, weight=1) 
            
            frame_coluna_wrapper = ctk.CTkFrame(self.frame_colunas, fg_color="transparent") 
            frame_coluna_wrapper.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            coluna_obj = ColunaKanban(frame_coluna_wrapper, status, self)
            coluna_obj.pack(fill="both", expand=True)
            self.colunas_ui[status] = coluna_obj
        
        self.frame_colunas.grid_rowconfigure(0, weight=1) 

        self.atualizar_quadro_kanban_ui()

    def mudar_tema(self):
        if self.switch_tema.get() == 1: 
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def limpar_filtros_pesquisa(self):
        self.entry_pesquisa.delete(0, tk.END)
        self.combobox_filtro_categoria.set("Todas")
        self.atualizar_quadro_kanban_ui()

    def abrir_dialogo_nova_tarefa(self):
        DialogoTarefa(self, self) 

    def mover_tarefa_logica(self, tarefa_info, direcao): 
        tarefa = encontrar_tarefa_por_id(tarefa_info["id"])
        if not tarefa: return

        status_atual = tarefa['status']
        try:
            index_atual = STATUS_COLUNAS.index(status_atual)
        except ValueError:
            return 

        novo_index = index_atual + direcao

        if 0 <= novo_index < len(STATUS_COLUNAS):
            tarefa['status'] = STATUS_COLUNAS[novo_index]
            salvar_tarefas_data()
            self.atualizar_quadro_kanban_ui()
            messagebox.showinfo("Sucesso", f"Tarefa movida para '{tarefa['status']}'.", parent=self)
        else:
            messagebox.showwarning("Movimento Inválido", "Não é possível mover a tarefa nessa direção.", parent=self)

    def atualizar_quadro_kanban_ui(self, event=None): # Adicionado event=None para o bind
        """Limpa todas as colunas e recarrega as tarefas com base nos filtros."""
        termo_pesquisa = self.entry_pesquisa.get().lower().strip()
        categoria_filtro = self.combobox_filtro_categoria.get()

        for status, coluna_ui_obj in self.colunas_ui.items():
            coluna_ui_obj.limpar_tarefas_ui()
        
        for tarefa in tarefas_data:
            # Aplicar filtro de categoria
            if categoria_filtro != "Todas" and tarefa.get("categoria") != categoria_filtro:
                continue # Pula esta tarefa se não corresponder ao filtro de categoria

            # Aplicar filtro de pesquisa
            if termo_pesquisa:
                titulo_match = termo_pesquisa in tarefa["titulo"].lower()
                descricao_match = termo_pesquisa in tarefa["descricao"].lower()
                if not (titulo_match or descricao_match):
                    continue # Pula esta tarefa se não corresponder ao termo de pesquisa
            
            # Se passou pelos filtros, adiciona à coluna correta
            status_tarefa = tarefa["status"]
            if status_tarefa in self.colunas_ui:
                self.colunas_ui[status_tarefa].adicionar_tarefa_ui(tarefa)

if __name__ == "__main__":
    app = KanbanApp()
    app.mainloop()
