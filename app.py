import streamlit as st
import pandas as pd
import geopandas as gp
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium
import mapclassify as mc
import branca.colormap as cm
from folium.plugins import LocateControl
import plotly.express as px
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="GH | Whobuys",
    page_icon="🛍️",
    layout="wide"
)

# Função para injetar CSS customizado
def inject_css():
    hide_st_style = """
            <style>
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    # Inserir CSS personalizado para alterar a cor da sidebar
    st.markdown("""
        <style>
        /* Alterar a cor da sidebar */
        .st-emotion-cache-6qob1r.eczjsme11 {
            background-color: #001c47;  /* Cor de fundo personalizada */
        }

        /* Alterar a cor do texto na sidebar */
        .st-emotion-cache-6qob1r.eczjsme11 h1, 
        .st-emotion-cache-6qob1r.eczjsme11 h2, 
        .st-emotion-cache-6qob1r.eczjsme11 h3, 
        .st-emotion-cache-6qob1r.eczjsme11 h4, 
        .st-emotion-cache-6qob1r.eczjsme11 h5, 
        .st-emotion-cache-6qob1r.eczjsme11 p {
            color: #ffff;  /* Cor do texto */
        }
        </style>
        """, unsafe_allow_html=True)

# Injetando CSS
inject_css()


# Login
names = ["Grupo Solano"]
usernames = ["gruposolano"]

file_path = Path(__file__).parent / "hashedpw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

# Criar um dicionário de credenciais
credentials = {
    "usernames": {
        usernames[0]: {  # "gruposolano"
            #"email": "gruposolano@gmail.com",
            "name": names[0],  # "Grupo Solano"
            "password": hashed_passwords[0]  # hash da senha correspondente
        }
    }
}

# Inicializar o autenticador com as credenciais corretas
authenticator = stauth.Authenticate(credentials, "whobuys", "random_key", cookie_expiry_days=30)
# Realiza o login com uma key única
# Realiza o login e captura o retorno
login_response = authenticator.login("main")

# Verifica se o login_response é None
if login_response is None:
    st.error("Erro de autenticação: Nenhum dado retornado. Verifique suas credenciais.")
else:
    # Desempacota os valores de retorno
    name, authenticator_status, username = login_response

    if authenticator_status == False:
        st.error("Username/password is incorrect")

    if authenticator_status is None:
        st.warning("Insira login e senha")

    if authenticator_status:

        whiteLogo = 'img/Main Logo White.png'
        blackLogo = 'img/Main Logo Black.png'
        iconLogo = 'img/White Icone.png'

        #Carregando Dados
        @st.cache_data()
        def carregarDados():
            malhaCenso2010 = gp.read_file('db/malha-censo2010/malha-censo2010.shp')
            malhaCenso2022 = gp.read_file('db/malha-censo2022/malha-censo2022.shp')
            cidadesLocalizacao = pd.read_csv('db/coordenadas_municipios_sp.csv')

            return malhaCenso2010, malhaCenso2022, cidadesLocalizacao
        @st.cache_data()
        def carregar_htmls():
            # Dicionário para armazenar os conteúdos dos HTMLs
            html_map = {
                'renda_media': 'db/censo-geral-2010/mapa_Rendimento.html',
                'raca_branca': 'db/censo-geral-2010/mapa_racaBranca.html',
                'raca_preta': 'db/censo-geral-2010/mapa_racaPreta.html',
                'raca_amarela': 'db/censo-geral-2010/mapa_racaAmarel.html',
                'raca_parda': 'db/censo-geral-2010/mapa_racaParda.html',
                'raca_indigena': 'db/censo-geral-2010/mapa_racaIndige.html',
                'mulheres_responsaveis': 'db/censo-geral-2010/mapa_mulheresRe.html',
                'avos': 'db/censo-geral-2010/mapa_avos.html',
                'jovens': 'db/censo-geral-2010/mapa_est. joven.html',
            }

            # Carregar os arquivos HTML e armazenar seu conteúdo
            html_content = {}
            for key, file_path in html_map.items():
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content[key] = f.read()

            return html_content

        # Chamando a função para usar no app
        malhaCenso2010, malhaCenso2022, cidadesLocalizacao, = carregarDados()
        html_content = carregar_htmls()

        if "malhaCenso2010" not in st.session_state:
            st.session_state["malhaCenso2010"] = malhaCenso2010
        if "malhaCenso2022" not in st.session_state:
            st.session_state["malhaCenso2022"] = malhaCenso2022
        if "cidadesLocalizacao" not in st.session_state:
            st.session_state["cidadesLocalizacao"] = cidadesLocalizacao

        # Definindo o menu com opções
        selecionado = option_menu(
            menu_title=None,
            options=['Home','Demografia Geral','Análise Demográfica','Suporte','Sair'],
            icons=["house","globe-americas",'geo-alt',"headset","box-arrow-right"],
            menu_icon='cast',
            default_index=0,
            orientation='horizontal',
        )

        # Conteúdo baseado na opção selecionada
        if selecionado == "Home":
            #st.write(f"### Bem-vindo {name}")
            st.image(blackLogo, width=200)  # Exibe o logo principal
            st.write('## Painel de dados') # Título da página no Streamlit
            # Ordenar os dados pela coluna de Rendimento
            df_sorted = malhaCenso2010.sort_values(by='Rendimento', ascending=False)
            # Criar o gráfico de barras com plotly.express
            fig = px.bar(df_sorted, x='NM_MUNICIP', y='Rendimento',
                         title='Municípios com mais renda por Domicílio',
                         labels={'NM_MUNICIP': 'Municípios', 'Rendimento': 'Renda Média'},
                         color='Rendimento', height=500)

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig)
            st.write('Dados do IBGE | Censo 2010')

            ag2022 = malhaCenso2022.groupby('NM_MUN')['v0001'].sum().reset_index()
            # Criar o gráfico de barras com plotly.express
            fig = px.bar(ag2022, x='NM_MUN', y='v0001',
                         title='Cidades com mais habitantes',
                         labels={'NM_MUN': 'Municípios', 'v0001': 'Nº de Habitantes'},
                         color='v0001', height=500)
            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig)
            st.write('Dados do IBGE | Censo 2022')

        elif selecionado == "Demografia Geral":
            coluna_mapeamento = {
                'Rendimento': 'Renda Média',
                'racaBranca': 'Distribuição por Cor/Raça Branca',
                'racaPreta': 'Distribuição por Cor/Raça Preta',
                'racaAmarel': 'Distribuição por Cor/Raça Amarela',
                'racaParda': 'Distribuição por Cor/Raça Parda',
                'racaIndige': 'Distribuição por Cor/Raça Indigena',
                'mulheresRe': 'Mulheres Responsáveis pelo Domicílio',
                'avos': 'Domicilio onde residem Avôs e/ou Avós',
                'est. joven': 'Estimativa de Domicílios onde residem Jovens de 18 anos',
            }
            # Mapeamento das opções para chaves de HTML
            html_map = {
                'Renda Média': 'renda_media',
                'Distribuição por Cor/Raça Branca': 'raca_branca',
                'Distribuição por Cor/Raça Preta': 'raca_preta',
                'Distribuição por Cor/Raça Amarela': 'raca_amarela',
                'Distribuição por Cor/Raça Parda': 'raca_parda',
                'Distribuição por Cor/Raça Indigena': 'raca_indigena',
                'Mulheres Responsáveis pelo Domicílio': 'mulheres_responsaveis',
                'Domicilio onde residem Avôs e/ou Avós': 'avos',
                'Estimativa de Domicílios onde residem Jovens de 18 anos': 'jovens',
            }
            opcoes = list(coluna_mapeamento.values())
            coluna_amigavel_selecionada = st.selectbox("Escolha a categoria para visualização", opcoes)
            # Obtenha a chave correspondente à opção selecionada
            chave_html_selecionada = html_map[coluna_amigavel_selecionada]
            # Exibir o conteúdo HTML correspondente
            st.components.v1.html(html_content[chave_html_selecionada], height=500)

        elif selecionado == "Análise Demográfica":
            with st.sidebar:
                st.image(whiteLogo, width=180)  # Exibe o logo principal
                cidade_selecionada = st.selectbox('Escolha uma Cidade para a Análise:',cidadesLocalizacao['Municipio'].unique())
                # Encontrar a latitude e longitude correspondentes ao município selecionado
                loc = cidadesLocalizacao[cidadesLocalizacao['Municipio'] == cidade_selecionada][['Latitude', 'Longitude']].values[0]
                coluna_mapeamento = {
                    'Rendimento': 'Renda Média',
                    'racaBranca': 'Distribuição por Cor/Raça Branca',
                    'racaPreta': 'Distribuição por Cor/Raça Preta',
                    'racaAmarel': 'Distribuição por Cor/Raça Amarela',
                    'racaParda': 'Distribuição por Cor/Raça Parda',
                    'racaIndige': 'Distribuição por Cor/Raça Indigena',
                    'mulheresRe': 'Mulheres Responsáveis pelo Domicílio',
                    'avos': 'Domicilio onde residem Avôs e/ou Avós',
                    'est. joven': 'Estimativa de Domicílios onde residem Jovens de 18 anos',
                }
                opcoes = list(coluna_mapeamento.values())
                coluna_amigavel_selecionada = st.selectbox("Escolha a categoria para visualização", opcoes)
            malhaCenso2010Filtrado = malhaCenso2010[malhaCenso2010['NM_MUNICIP'] == cidade_selecionada]
            coluna_selecionada = [k for k, v in coluna_mapeamento.items() if v == coluna_amigavel_selecionada][0]
            # Dicionário de colormaps para cada variável
            colormap_dict = {
                'Rendimento': cm.linear.YlGn_09,
                'racaBranca': cm.linear.Reds_09,
                'racaPreta': cm.linear.Blues_09,
                'racaAmarel': cm.linear.Oranges_09,
                'racaParda': cm.linear.Purples_09,
                'racaIndige': cm.linear.Greens_09,
                'mulheresRe': cm.linear.PuRd_09,
                'avos': cm.linear.Greys_09,
                'est. joven': cm.linear.Blues_09,
                'SomaSemIlu': cm.linear.YlOrRd_09,
                'SomaSemPav': cm.linear.YlGnBu_09,
                'SomaSemCal': cm.linear.YlOrBr_09,
                'Domicilio_': cm.linear.BuPu_09,
            }
            # Seleciona o colormap com base na variável escolhida
            colormap = colormap_dict[coluna_selecionada].scale(malhaCenso2010Filtrado[coluna_selecionada].min(),
                                                               malhaCenso2010Filtrado[coluna_selecionada].max())
            colormap = colormap.to_step(n=6)

            ### Mapa ###
            st.write(f"### {coluna_amigavel_selecionada}")
            # E a coluna que você quer usar para coloração seja 'V005'
            column = coluna_selecionada
            # Classificação dos dados em quantis
            quantiles = mc.Quantiles(malhaCenso2010Filtrado[column], k=4)
            # Função para determinar o estilo dos polígonos
            def style_function(feature):
                value = feature['properties'][column]
                return {
                    'fillColor': colormap(value),
                    'color': 'black',
                    'weight': 0.2,
                    'fillOpacity': 0.8,
                }
            # Criar o mapa centrado em uma localização específica
            m = folium.Map(location=loc, zoom_start=12)
            # Adicionar as geometrias ao mapa com estilo
            folium.GeoJson(
                malhaCenso2010Filtrado.to_json(),
                style_function=style_function
            ).add_to(m)
            LocateControl(
                position="topleft",  # Posição do botão no mapa
                strings={"title": "Mostrar minha localização"},  # Texto de dica quando se passa o mouse
                flyTo=True,  # Se deve mover o mapa para a localização encontrada
            ).add_to(m)
            # Adicionar a legenda ao mapa
            colormap.caption = coluna_amigavel_selecionada
            colormap.add_to(m)
            # Adicionar manualmente etiquetas
            folium.LayerControl().add_to(m)
            # Exibir o mapa
            st_folium(m, width=900, height=600)
            st.write('Dados do IBGE | Censo 2010')


        elif selecionado == "Suporte":
            # Criar um botão com ícone do WhatsApp e link para abrir a conversa
            # Número do WhatsApp
            numero_whatsapp = '18991610757'  # Substitua pelo número real
            # Escrever o link com um botão que abre em uma nova aba
            st.write(f'''
                <a target="_blank" href="https://wa.me/{numero_whatsapp}">
                    <button style="background-color: #ffff; color: #25D366 ; border: 2px solid #25D366; padding: 10px 20px; border-radius: 20px; cursor: pointer;">
                         Clique aqui e Fale com um atendente 📱
                    </button>
                </a>
                ''',
                     unsafe_allow_html=True
                     )
        elif selecionado == "Sair":
            authenticator.logout("Sair", "main")