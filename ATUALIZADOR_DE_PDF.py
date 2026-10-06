# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'ATUALIZADOR DE PDF.py'
# Bytecode version: 3.12.0rc2 (3531)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import os
import sys
import shutil
import logging
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
import customtkinter as ctk
from tkinter import filedialog, messagebox
ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')
class TextHandler(logging.Handler):
    """Handler personalizado para redirecionar os logs para a caixa de texto da interface."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert('end', msg + '\n')
            self.text_widget.see('end')
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)
class AppProcessadorPDF(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Processador de Atualização de PDFs - Mapas')
        self.geometry('780x680')
        self.minsize(700, 600)
        self.pasta_base = ctk.StringVar()
        self.pasta_atualizacao = ctk.StringVar()
        self._criar_interface()
        self._configurar_logging()
    def _criar_interface(self):
        frame_pastas = ctk.CTkFrame(self)
        frame_pastas.pack(padx=20, pady=(20, 10), fill='x')
        lbl_base = ctk.CTkLabel(frame_pastas, text='Pasta Oficial (Base):', font=('Arial', 12, 'bold'))
        lbl_base.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='w')
        ent_base = ctk.CTkEntry(frame_pastas, textvariable=self.pasta_base, width=480)
        ent_base.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='ew')
        btn_base = ctk.CTkButton(frame_pastas, text='Buscar Pasta', command=self.selecionar_pasta_base)
        btn_base.grid(row=1, column=1, padx=10, pady=(0, 10))
        lbl_atualizacao = ctk.CTkLabel(frame_pastas, text='Pasta de Atualização (PG2, PG3, CANA COMPRA):', font=('Arial', 12, 'bold'))
        lbl_atualizacao.grid(row=2, column=0, padx=10, pady=(10, 5), sticky='w')
        ent_atualizacao = ctk.CTkEntry(frame_pastas, textvariable=self.pasta_atualizacao, width=480)
        ent_atualizacao.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
        btn_atualizacao = ctk.CTkButton(frame_pastas, text='Buscar Pasta', command=self.selecionar_pasta_atualizacao)
        btn_atualizacao.grid(row=3, column=1, padx=10, pady=(0, 10))
        frame_pastas.columnconfigure(0, weight=1)
        self.btn_iniciar = ctk.CTkButton(self, text='🚀 INICIAR PROCESSAMENTO', font=('Arial', 14, 'bold'), fg_color='#1f6aa5', hover_color='#144870', height=45, command=self.iniciar_processamento)
        self.btn_iniciar.pack(padx=20, pady=10, fill='x')
        lbl_log = ctk.CTkLabel(self, text='Log de Execução:', font=('Arial', 12, 'bold'))
        lbl_log.pack(padx=20, pady=(10, 0), anchor='w')
        self.txt_log = ctk.CTkTextbox(self, font=('Consolas', 11), state='disabled')
        self.txt_log.pack(padx=20, pady=(5, 20), fill='both', expand=True)
    def _configurar_logging(self):
        self.logger = logging.getLogger('PDFProcessor')
        self.logger.setLevel(logging.INFO)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        handler = TextHandler(self.txt_log)
        formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    def selecionar_pasta_base(self):
        pasta = filedialog.askdirectory(title='Selecione a Pasta Oficial (Base)')
        if pasta:
            self.pasta_base.set(pasta)
    def selecionar_pasta_atualizacao(self):
        pasta = filedialog.askdirectory(title='Selecione a Pasta com os Arquivos de Atualização')
        if pasta:
            self.pasta_atualizacao.set(pasta)
    def criar_backup(self, caminho_arquivo, backup_dir, subpasta_backup=''):
        destino_pasta = os.path.join(backup_dir, subpasta_backup)
        os.makedirs(destino_pasta, exist_ok=True)
        nome_arquivo = os.path.basename(caminho_arquivo)
        caminho_backup = os.path.join(destino_pasta, nome_arquivo)
        try:
            shutil.copy2(caminho_arquivo, caminho_backup)
            self.logger.info(f'🗂️ Backup criado em: {caminho_backup}')
        except Exception as e:
            self.logger.error(f'❌ Erro ao criar backup de {nome_arquivo}: {e}')
    def substituir_paginas(self, caminho_base, caminho_atualizacao, paginas_para_substituir, backup_dir, subpasta_backup=''):
        if not os.path.exists(caminho_base):
            self.logger.warning(f'⚠️ Arquivo base não encontrado: {os.path.basename(caminho_base)}')
            return
        else:
            try:
                self.criar_backup(caminho_base, backup_dir, subpasta_backup=subpasta_backup)
                pdf_base = PdfReader(caminho_base)
                pdf_atualizacao = PdfReader(caminho_atualizacao)
                pdf_saida = PdfWriter()
                num_paginas_base = len(pdf_base.pages)
                num_paginas_atualizacao = len(pdf_atualizacao.pages)
                usar_indice_direto = num_paginas_atualizacao >= num_paginas_base
                idx_atualizacao = 0
                for i in range(num_paginas_base):
                    pagina_num = i + 1
                    if pagina_num in paginas_para_substituir:
                        target_idx = i if usar_indice_direto else idx_atualizacao
                        if target_idx < num_paginas_atualizacao:
                            pagina_substituta = pdf_atualizacao.pages[target_idx]
                            pdf_saida.add_page(pagina_substituta)
                            self.logger.info(f'  -> Página {pagina_num} substituída em {os.path.basename(caminho_base)}')
                            idx_atualizacao += 1
                        else:
                            self.logger.warning(f'⚠️ Atualização sem páginas suficientes para PG {pagina_num}. Mantida original.')
                            pdf_saida.add_page(pdf_base.pages[i])
                    else:
                        pdf_saida.add_page(pdf_base.pages[i])
                with open(caminho_base, 'wb') as f_saida:
                    pdf_saida.write(f_saida)
                self.logger.info(f'✅ Atualizado com sucesso: {os.path.basename(caminho_base)}')
            except Exception as e:
                self.logger.error(f'❌ Erro ao processar {os.path.basename(caminho_base)}: {e}')
    def iniciar_processamento(self):
        base_dir = self.pasta_base.get()
        atualizacao_dir = self.pasta_atualizacao.get()
        if not base_dir or not os.path.exists(base_dir):
            messagebox.showerror('Erro', 'Selecione uma pasta Oficial (Base) válida!')
            return
        else:
            if not atualizacao_dir or not os.path.exists(atualizacao_dir):
                messagebox.showerror('Erro', 'Selecione uma pasta de Atualização válida!')
                return
            else:
                self.btn_iniciar.configure(state='disabled')
                backup_dir = os.path.join(base_dir, 'Backup')
                self.logger.info('=== INICIANDO PROCESSAMENTO DE PDFS ===')
                rotinas = [{'pasta': os.path.join(atualizacao_dir, 'PG2'), 'paginas': [2], 'subpasta_bck': '', 'nome': 'PG2'}, {'pasta': os.path.join(atualizacao_dir, 'PG3'), 'paginas': [2, 3], 'subpasta_bck': '', 'nome': 'PG3'}, {'pasta': os.path.join(atualizacao_dir, 'CANA COMPRA'), 'paginas': [2], 'subpasta_bck': 'CANA COMPRA', 'nome': 'CANA COMPRA'}]
                for rotina in rotinas:
                    pasta_origem = rotina['pasta']
                    if os.path.exists(pasta_origem):
                        self.logger.info(f"\n🔧 Processando pasta: {rotina['nome']}...")
                        for arquivo in os.listdir(pasta_origem):
                            if arquivo.lower().endswith('.pdf'):
                                if rotina['nome'] == 'CANA COMPRA':
                                    caminho_base = os.path.join(base_dir, 'CANA COMPRA', arquivo)
                                else:
                                    caminho_base = os.path.join(base_dir, arquivo)
                                caminho_atualizacao = os.path.join(pasta_origem, arquivo)
                                self.substituir_paginas(caminho_base, caminho_atualizacao, paginas_para_substituir=rotina['paginas'], backup_dir=backup_dir, subpasta_backup=rotina['subpasta_bck'])
                    else:
                        self.logger.warning(f"ℹ️ Pasta {rotina['nome']} não encontrada dentro da pasta de atualização.")
                self.logger.info('\n🚀 Processo concluído com sucesso!')
                self.btn_iniciar.configure(state='normal')
                messagebox.showinfo('Sucesso', 'Processamento finalizado!')
if __name__ == '__main__':
    app = AppProcessadorPDF()
    app.mainloop()
