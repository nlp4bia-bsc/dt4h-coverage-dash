from dash import html

MAIN_PAR_STYLE = {
                        "color": "#333",
                        "fontSize": "20px",
                        "textAlign": "center",
                        "lineHeight": "1.8",
                        "fontFamily": "Georgia, serif",
                        "marginBottom": "10px"
                    }

PAR_STYLE = {
    "color": "#333",
    "fontSize": "16px",
    "textAlign": "justify",
    "lineHeight": "1.6",
    "fontFamily": "Georgia, serif",
    "marginBottom": "10px"
}

TOP_DIV = html.Div(
            children=[
                    html.Img(
                            src="assets/BSC-blue-small.png",  # Replace with your image URL
                            style={
                                "height": "80px",
                                "width": "300px",
                                "float": "left",
                            }
                        ),
                html.H1(
                    "Variable Coverage Analysis App",
                    style={
                        "color": "#1e0099",
                        "fontSize": "48px",
                        "textAlign": "center",
                        "fontFamily": "Arial, sans-serif",
                        "marginBottom": "20px",
                        "marginTop": "80px"
                    }
                ),
                html.P(
                    "Before normalization is done, it is a common process to study the level of coverage or agreement between our resources and the main variables defined by the clinicians. This is performed by selecting our corpora for the most important entity types (usually disease, symptom, drug and procedure) and compare available codes with the ones in the clinical variables list.",
                    style=PAR_STYLE
                ),
            ],
            style={
                "backgroundColor": "#f9f9f9",
                "padding": "30px",
                "borderRadius": "10px",
                "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.1)",
                "marginBottom": "40px"
            }
        )
