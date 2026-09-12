"""
============================================================
HORTA DO FUTURO
DIGITAL TWIN - MOTOR BIOLÓGICO COM SUPORTE A ESP32
============================================================
"""
import json
import urllib.request
from modelo.configuracao import ConfiguracaoCultivo
from modelo.relogio_virtual import RelogioVirtual
from modelo.banco_cultivos import obter_configuracao_cultura

class Horta:

    FASES_VALIDAS = (
        "MUDA",
        "VEGETATIVO",
        "FLORAÇÃO / FRUTIFICAÇÃO",
    )

    def __init__(self):
        self.config = obter_configuracao_cultura("ALFACE")
        self.cultivo = getattr(self.config, "nome", getattr(self.config, "nome_cultivo", "ALFACE"))

        # Reservatório
        self.capacidade_reservatorio_ml = 10000.0
        self.volume_solucao_ml = self.capacidade_reservatorio_ml
        self.nivel_agua = 100.0

        # Configuração do Fertilizante
        self.nome_fertilizante = "Flex Azul + Vermelho (A+B)"
        self.gramas_por_litro_recomendado = 0.84  
        self.taxa_ph_down = 0.5       
        self.taxa_ph_up = 0.5         

        # Sensores
        self.temperatura_ar = 24.5
        self.umidade_ar = 60.0
        self.temperatura_agua = 22.0
        self.ph = 6.0
        self.ec = 1.4

        # Nutrição & Saúde
        self.historico_dosagem = []
        self.saude = 100.0
        self.status = "SAUDÁVEL"
        self.alertas = []

        # Atuadores e Dimmer / PWM
        self.ventilacao = False
        self.bomba = False
        self.iluminacao = False
        self.intensidade_iluminacao_pwm = 0
        self.dimmer_manual_nivel = 100.0
        self.modo_dimmer_manual = False

        # Endpoint do ESP32 (Modo Físico)
        self.esp32_ip = "http://192.168.4.1/config"

        # Relógio
        self.relogio = RelogioVirtual(hora=13, minuto=0)

        self._atualizar_nivel_agua()
        self.diagnosticar(minutos_decorridos=0)
        self.atualizar_fotoperiodo()

    @property
    def hora_atual(self):
        return self.relogio.hora

    @property
    def minuto_atual(self):
        return self.relogio.minuto

    @property
    def velocidade_tempo(self):
        return self.relogio.velocidade

    def definir_hora(self, hora, minuto):
        self.relogio.definir_hora(hora, minuto)
        self.atualizar_fotoperiodo()

    def avancar_tempo(self, minutos):
        self.relogio.avancar(minutos)
        self.atualizar_fotoperiodo()
        if self.automacao_ativa_interna():
            self.executar_automacao()
        self.diagnosticar(minutos_decorridos=abs(minutos))

    def configurar_velocidade_tempo(self, velocidade):
        self.relogio.configurar_velocidade(velocidade)

    def tick_tempo(self):
        minutos_passados = self.relogio.velocidade
        self.relogio.tick()
        self.atualizar_fotoperiodo()
        self.executar_automacao()
        self.diagnosticar(minutos_decorridos=minutos_passados)

    def automacao_ativa_interna(self):
        return True

    def alterar_temperatura_ar(self, valor):
        self.temperatura_ar = float(valor)

    def alterar_umidade_ar(self, valor):
        self.umidade_ar = float(valor)

    def alterar_temperatura_agua(self, valor):
        self.temperatura_agua = float(valor)

    def alterar_ph(self, valor):
        self.ph = float(valor)

    def alterar_ec(self, valor):
        self.ec = float(valor)

    def alterar_dimmer(self, valor):
        self.dimmer_manual_nivel = float(valor)
        if self.modo_dimmer_manual and self.iluminacao:
            self.intensidade_iluminacao_pwm = int(self.dimmer_manual_nivel)

    def alterar_nivel_agua(self, valor):
        valor = float(valor)
        self.nivel_agua = max(0.0, min(100.0, valor))
        self.volume_solucao_ml = (self.capacidade_reservatorio_ml * self.nivel_agua / 100.0)
        if self.nivel_agua <= 10:
            self.desligar_bomba()

    def _atualizar_nivel_agua(self):
        if self.capacidade_reservatorio_ml <= 0:
            self.volume_solucao_ml = 0.0
            self.nivel_agua = 0.0
            return
        self.volume_solucao_ml = max(0.0, min(self.capacidade_reservatorio_ml, float(self.volume_solucao_ml)))
        self.nivel_agua = (self.volume_solucao_ml / self.capacidade_reservatorio_ml * 100.0)

    def nivel_agua_status(self):
        if self.nivel_agua <= 0:
            return "VAZIO"
        if self.nivel_agua <= 25:
            return "CRÍTICO"
        if self.nivel_agua <= 50:
            return "BAIXO"
        return "ADEQUADO"

    def calcular_receita_dosagem(self):
        litros_atuais = max(0.5, self.volume_solucao_ml / 1000.0)
        ec_alvo = (self.config.ec_min + self.config.ec_max) / 2.0
        ph_alvo = (self.config.ph_min + self.config.ph_max) / 2.0

        diferenca_ec = max(0.0, ec_alvo - self.ec)
        diferenca_ph = self.ph - ph_alvo

        gramas_totais = diferenca_ec * self.gramas_por_litro_recomendado * litros_atuais
        
        if diferenca_ph > 0.2:
            dose_ph_down_ml = round(diferenca_ph * self.taxa_ph_down * litros_atuais, 1)
            dose_ph_up_ml = 0.0
        elif diferenca_ph < -0.2:
            dose_ph_up_ml = round(abs(diferenca_ph) * self.taxa_ph_up * litros_atuais, 1)
            dose_ph_down_ml = 0.0
        else:
            dose_ph_down_ml = 0.0
            dose_ph_up_ml = 0.0

        return {
            "nome_fertilizante": self.nome_fertilizante,
            "quantidade_total_g": round(gramas_totais, 1),
            "ph_down_ml": dose_ph_down_ml,
            "ph_up_ml": dose_ph_up_ml,
            "volume_litros": round(litros_atuais, 1)
        }

    def aplicar_dosagem(self, produto, quantidade):
        produto = str(produto).strip().upper()
        quantidade = float(quantidade)
        if quantidade <= 0:
            return

        litros = max(0.5, self.volume_solucao_ml / 1000.0)
        if "FERTILIZANTE" in produto or "NUTRIENTE" in produto:
            self.ec = round(self.ec + (quantidade / (self.gramas_por_litro_recomendado * litros)), 2)
        elif produto == "PH_DOWN":
            self.ph = round(max(2.0, self.ph - (quantidade / (self.taxa_ph_down * litros))), 1)
        elif produto == "PH_UP":
            self.ph = round(min(12.0, self.ph + (quantidade / (self.taxa_ph_up * litros))), 1)

        evento = {
            "produto": produto,
            "quantidade": quantidade,
            "ec_resultante": self.ec,
            "ph_resultante": self.ph
        }
        self.historico_dosagem.append(evento)
        self.diagnosticar()

    def atualizar_fotoperiodo(self):
        inicio_minutos = self.config.inicio_luz_hora * 60 + self.config.inicio_luz_minuto
        duracao_luz_minutos = int(round(self.config.fotoperiodo_horas * 60))
        fim_minutos = (inicio_minutos + duracao_luz_minutos) % 1440
        agora_minutos = self.hora_atual * 60 + self.minuto_atual

        rampa_minutos = 15

        no_horario_luz = False
        if inicio_minutos < fim_minutos:
            no_horario_luz = inicio_minutos <= agora_minutos < fim_minutos
        else:
            no_horario_luz = agora_minutos >= inicio_minutos or agora_minutos < fim_minutos

        teto_intensidade = self.dimmer_manual_nivel if self.modo_dimmer_manual else 100.0

        if no_horario_luz:
            minutos_desde_inicio = (agora_minutos - inicio_minutos) % 1440
            if minutos_desde_inicio < rampa_minutos:
                self.intensidade_iluminacao_pwm = int(teto_intensidade * (minutos_desde_inicio / rampa_minutos))
            else:
                minutos_ate_fim = (fim_minutos - agora_minutos) % 1440
                if minutos_ate_fim < rampa_minutos:
                    self.intensidade_iluminacao_pwm = int(teto_intensidade * (minutos_ate_fim / rampa_minutos))
                else:
                    self.intensidade_iluminacao_pwm = int(teto_intensidade)
            self.iluminacao = self.intensidade_iluminacao_pwm > 0
        else:
            minutos_ate_inicio = (inicio_minutos - agora_minutos) % 1440
            if minutos_ate_inicio < rampa_minutos:
                progresso = 1.0 - (minutos_ate_inicio / rampa_minutos)
                self.intensidade_iluminacao_pwm = int(teto_intensidade * progresso)
                self.iluminacao = self.intensidade_iluminacao_pwm > 0
            else:
                self.intensidade_iluminacao_pwm = 0
                self.iluminacao = False

    def esta_no_periodo_luz(self):
        inicio = self.config.inicio_luz_hora * 60 + self.config.inicio_luz_minuto
        duracao = int(round(self.config.fotoperiodo_horas * 60))
        agora = self.hora_atual * 60 + self.minuto_atual
        if duracao >= 1440:
            return True
        if duracao <= 0:
            return False
        fim = (inicio + duracao) % 1440
        if inicio < fim:
            return inicio <= agora < fim
        return agora >= inicio or agora < fim

    def aplicar_configuracao(self, configuracao, enviar_para_esp32=False):
        if not isinstance(configuracao, ConfiguracaoCultivo):
            raise TypeError("A configuração deve ser uma ConfiguracaoCultivo.")
        self.config = configuracao
        self.cultivo = getattr(configuracao, "nome", getattr(configuracao, "nome_cultivo", self.cultivo))
        self.diagnosticar(minutos_decorridos=0)
        self.atualizar_fotoperiodo()

        if enviar_para_esp32:
            self.sincronizar_com_esp32()

    def sincronizar_com_esp32(self):
        try:
            payload = json.dumps(self.config.snapshot()).encode("utf-8")
            req = urllib.request.Request(
                self.esp32_ip, 
                data=payload, 
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2) as response:
                print("📡 Sincronizado com sucesso com o ESP32:", response.read().decode())
        except Exception as e:
            print("⚠️ Aviso: Não foi possível conectar ao ESP32 físico:", e)

    def selecionar_cultura(self, nome):
        configuracao = obter_configuracao_cultura(nome)
        self.aplicar_configuracao(configuracao)

    def ligar_ventilacao(self):
        self.ventilacao = True

    def desligar_ventilacao(self):
        self.ventilacao = False

    def ligar_bomba(self):
        if self.nivel_agua > 10:
            self.bomba = True
        else:
            self.bomba = False

    def desligar_bomba(self):
        self.bomba = False

    def diagnosticar(self, minutos_decorridos=0):
        taxa_estresse = 0.0
        self.alertas = []

        if self.saude <= 0:
            self.saude = 0.0
            self.status = "PLANTA MORTA"
            self.alertas = ["🚨 Cultivo perdido por estresse severo!"]
            return 0.0

        if self.nivel_agua <= 0:
            taxa_estresse += 0.20
            self.alertas.append("⚠️ Sem água no reservatório")
        elif self.nivel_agua <= 20:
            taxa_estresse += 0.05
            self.alertas.append("⚠️ Nível de água baixo")

        if self.ph < self.config.ph_min:
            taxa_estresse += 0.05
            self.alertas.append("⚠️ pH ácido (Necessita pH Up)")
        elif self.ph > self.config.ph_max:
            taxa_estresse += 0.05
            self.alertas.append("⚠️ pH alcalino (Necessita pH Down)")

        if self.ec < self.config.ec_min:
            taxa_estresse += 0.05
            self.alertas.append("⚠️ Falta nutrientes (Adicione Fertilizante)")
        elif self.ec > self.config.ec_max:
            taxa_estresse += 0.06
            self.alertas.append("⚠️ Excesso de sais (Adicione água pura)")

        if self.temperatura_ar < self.config.temperatura_ar_min or self.temperatura_ar > self.config.temperatura_ar_max:
            taxa_estresse += 0.04
            self.alertas.append("⚠️ Temp. do ar inadequada")

        if self.temperatura_agua < self.config.temperatura_agua_min or self.temperatura_agua > self.config.temperatura_agua_max:
            taxa_estresse += 0.08
            self.alertas.append("⚠️ Temp. da água inadequada")

        if taxa_estresse > 0:
            fator_tempo = max(1.0, minutos_decorridos)
            dano = taxa_estresse * fator_tempo * 1.5
            self.saude = max(0.0, self.saude - dano)
        else:
            if minutos_decorridos > 0:
                self.saude = min(100.0, self.saude + (0.05 * minutos_decorridos))

        if self.saude <= 0:
            self.status = "PLANTA MORTA"
        elif self.saude < 25:
            self.status = "CRÍTICO"
        elif self.saude < 60:
            self.status = "ATENÇÃO"
        elif self.saude < 85:
            self.status = "BOA"
        else:
            self.status = "SAUDÁVEL"

        return round(self.saude, 1)

    def executar_automacao(self):
        if self.temperatura_ar > self.config.temperatura_ar_max:
            self.ligar_ventilacao()
        else:
            self.desligar_ventilacao()

        if self.nivel_agua <= 10:
            self.desligar_bomba()

        self.atualizar_fotoperiodo()

    def resetar(self):
        self.temperatura_ar = 24.5
        self.umidade_ar = 60.0
        self.temperatura_agua = 22.0
        self.ph = 6.0
        self.ec = 1.4

        self.capacidade_reservatorio_ml = 10000.0
        self.volume_solucao_ml = self.capacidade_reservatorio_ml
        self.nivel_agua = 100.0

        self.historico_dosagem = []
        self.saude = 100.0
        self.status = "SAUDÁVEL"
        self.alertas = []

        self.ventilacao = False
        self.bomba = False
        self.iluminacao = False
        self.intensidade_iluminacao_pwm = 0
        self.dimmer_manual_nivel = 100.0
        self.modo_dimmer_manual = False

        self.relogio.definir_hora(13, 0)
        self.relogio.configurar_velocidade(1)

        self._atualizar_nivel_agua()
        self.diagnosticar(minutos_decorridos=0)
        self.atualizar_fotoperiodo()

    def snapshot(self):
        nome_cultivo = getattr(self.config, "nome_cultivo", getattr(self.config, "nome", self.cultivo))
        return {
            "cultivo": self.cultivo,
            "nome_cultivo": nome_cultivo,
            "fase": self.config.fase,
            "temperatura_ar": self.temperatura_ar,
            "umidade_ar": self.umidade_ar,
            "temperatura_agua": self.temperatura_agua,
            "ph": self.ph,
            "ec": self.ec,
            "capacidade_reservatorio_ml": self.capacidade_reservatorio_ml,
            "volume_solucao_ml": self.volume_solucao_ml,
            "nivel_agua": self.nivel_agua,
            "nivel_agua_status": self.nivel_agua_status(),
            "dosagem_recomendada": self.calcular_receita_dosagem(),
            "historico_dosagem": list(self.historico_dosagem),
            "saude": round(self.saude, 1),
            "status": self.status,
            "alertas": self.alertas,
            "ventilacao": self.ventilacao,
            "bomba": self.bomba,
            "iluminacao": self.iluminacao,
            "intensidade_iluminacao_pwm": self.intensidade_iluminacao_pwm,
            "fotoperiodo_horas": self.config.fotoperiodo_horas,
            "inicio_luz_hora": self.config.inicio_luz_hora,
            "inicio_luz_minuto": self.config.inicio_luz_minuto,
            "hora_atual": self.hora_atual,
            "minuto_atual": self.minuto_atual,
            "periodo_luz": self.esta_no_periodo_luz(),
            "velocidade_tempo": self.velocidade_tempo,
            "configuracao": self.config.snapshot(),
        }