## FYI you would not want to design a shiny app this way. It is written so you can run the R code first, 
## then it pushes all the variables into the R Shiny section to build the GUI.

###########################################
### Fail safe install and load packages ###
###########################################
  list.of.packages <- c('fireData', 'ggplot2', 'reshape2', 'dplyr', 'plotly', 'corrplot', 'RColorBrewer', 'pacman', 'DT', 'shiny','shinydashboard')
  new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
  if(length(new.packages)){
    install.packages(new.packages[new.packages!='fireData'])
    if('fireData' %in% new.packages) {
      if (!require("devtools")) install.packages("devtools")
      devtools::install_github("Kohze/fireData")
    }
  }
  pacman::p_load('fireData', 'ggplot2', 'ggplot2', 'reshape2', 'dplyr', 'plotly', 'corrplot', 'RColorBrewer', 'DT', 'shiny','shinydashboard')


options(shiny.trace = TRUE)
########################
# Pull Data From Cloud #
########################
  #######################
  ## Data from Sensors ##
  #######################
    from.cloud = download(projectURL = "https://fish-tank-e191b.firebaseio.com/Data", fileName = "")
    num.years <- length(from.cloud)
    temp.sensor.data <- do.call(rbind.data.frame, from.cloud)
    sensor.data <- filter(temp.sensor.data, duplicated(temp.sensor.data$Time)!=T)
      row.names(sensor.data) <- sensor.data$Time
  
    ### Break up date and time
      tmp <- do.call(
                rbind.data.frame,
                lapply(
                  strsplit(as.character(sensor.data$Time), split = " "),
                  function(x){
                    data.frame( x[1], x[2])
                  }
                )
              )            
      if(all.equal.character(rownames(sensor.data),paste(tmp[,1], tmp[,2], sep = " "))!=T) stop("Date times aren't aligned")
        sensor.data$Time <- as.POSIXct(sensor.data$Time)
        
      #### Data for server analysis    
        sensor.data.new <- data.frame(Date=tmp[,1], Time=tmp[,2], sensor.data, stringsAsFactors = F)
          sensor.data.new$Leak1 <- round(sensor.data.new$Leak1,3)*100
          sensor.data.new$Leak2 <- round(sensor.data.new$Leak2,3)*100
          sensor.data.new$Water <- round(sensor.data.new$Water,3)*100
          sensor.data.new$Light <- round(sensor.data.new$Light,3)*100
  ##################      
  ## Weather Data ##
  ##################
    conditions = download(projectURL = "https://fish-tank-e191b.firebaseio.com/Condition", fileName = "")
      weather <- conditions$main
    ### Determine Icon
      if(weather=="Clear"){
        weather.icon = "sun-o"
      } else if(weather == "Rain"){
        weather.icon = "shower"
      } else if(weather == "Drizzle"){
        weather.icon = "shower"
      } else if(weather == "Clouds"){
        weather.icon = "cloud"
      } else if(weather == "Thunderstorm"){
        weather.icon = "bolt"
      } else{
        weather.icon = "thumbs"
      }


###########################
## User Interface Layout ##
###########################

  sidebar <- dashboardSidebar(
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("dashboard"), badgeColor = 'blue'),
      menuItem("Historical Data", icon = icon("calendar"), tabName = "historicaldata", badgeColor = "green"),
      menuItem("Analyze Data", tabName = 'analyzedata', icon = icon("server")),
      menuItem('About Project', tabName = 'overview', icon = icon('info'))
    )
  )
  
  body <- dashboardBody(
    tabItems(
      tabItem(tabName = "dashboard",
        h2("Today"),
          fluidRow(
              column(
                  width = 11, offset = 1,
                  valueBoxOutput("weather.box"),
                  valueBoxOutput("tank.box"),
                  valueBoxOutput("room.box")
              )
          ),
          fluidRow(
              column (
                  width = 12, offset = 0, 
                  valueBoxOutput('water.level',width = 3),
                  valueBoxOutput("light.box", width = 3),
                  valueBoxOutput('leak1', width = 3),
                  valueBoxOutput('leak2', width = 3),
                  br(), br(), br()
              )            
          ),
          fluidRow(
            br(), br(),
            box(
                #title = "Today's Temperature Data", 
                status = "primary", plotlyOutput("today", width = "100%", height = "500px"),
                width = 12
            )
          ),
          fluidRow(
              column(12, offset=0, br(), br(), 
              tabPanel("Temperature Summary", dataTableOutput("todaytable"))
              )
          )
      ),
      tabItem(tabName = "historicaldata",
        h2("Historical Data"),
        fluidRow(
          box(
              #title = "Today's Temperature Data",
              status = "primary", plotlyOutput("historic", width = "100%", height = "780px"),
              width = 12
          )
        ),
        fluidRow(
          column(
            12, offset = 0, br(), br(),
            tabPanel("Historic Data Table", dataTableOutput('historictable'))
          )
        )
      ),
      tabItem(
        tabName = "analyzedata",
        h2(strong("Analyze Data")),
        fluidRow(
          column(
            width = 12, offset = 0,
            box(
              width = 12,
              title = "Correlation plot of variables",
              status = 'success',
              plotOutput('corplot')
            )
          )
        )
      ),
     tabItem(
       tabName = 'overview',
       h2(strong('Project Overview')),
       #tags$img(src='workflow.png', width = 1000) # uncomment this line if you want the image to load in
     )
    )
  )

###################
### UI Bundling ###
###################

ui <- dashboardPage(
  dashboardHeader(title = "Fish Tank Monitor"),
  sidebar,
  body
) 
        
#################################
### Server Side Functionality ###
#################################
        
server <- function(input, output) {
  
  ################
  # Output Boxes #
  ################
    output$weather.box <- renderValueBox({
          valueBox(
              weather, "Current Condition:", icon = icon(weather.icon),
              color = "yellow"
          )
      })
      output$water.level <- renderValueBox({
        water.level <- round(sensor.data.new$Water[nrow(sensor.data.new)],1)
          valueBox(
              paste(water.level,"%", sep=""), "% Water Level:", icon = icon("flask"),
              color = "blue"
          )
      })
      output$light.box <- renderValueBox({
        light <- round(sensor.data.new$Light[nrow(sensor.data.new)],1)
          valueBox(
              paste(light, "%", sep=""), "% Light Saturation:", icon = icon("power-off"),
              color = if(sensor.data.new$Light[nrow(sensor.data.new)]>0.3){
                "green"
              } else{
                "red"
              }
          )
      })
      output$leak1 <- renderValueBox({
        leak1 <- round(sensor.data.new$Leak1[nrow(sensor.data.new)],1)
          valueBox(
              paste(leak1, "%", sep=""), "% Front Leak Sensor:", icon = icon("tint"),
              color = if(leak1<20){
                "green"
              } else{
                "red"
              }
          )
      })
      output$leak2 <- renderValueBox({
        leak2 <- round(sensor.data.new$Leak1[nrow(sensor.data.new)],1)
          valueBox(
              paste(leak2, "%", sep=""), "% Rear Leak Sensor:", icon = icon("tint"),
              color = if(leak2<20){
                "green"
              } else{
                "red"
              }
          )
      })
      output$tank.box <- renderValueBox({
          valueBox(
              paste(round(sensor.data.new$Tank.Temp[nrow(sensor.data.new)],2),"°F", sep = ""), "Tank Temperature:", icon = icon("thermometer-full"),
              color = "light-blue"
          )
      })
      output$room.box <- renderValueBox({
          valueBox(
              paste(round(sensor.data.new$Ambient.Temp[nrow(sensor.data.new)],1), "°F", sep =""), "Room Temperature:", icon = icon("thermometer-3"),
              color = "purple"
          )
      })
      
    ##########
    # Tables #
    ##########
    output$todaytable <- renderDataTable({
      datatable(
        subset(sensor.data.new[which(format(sensor.data.new$Date, format = "%y")==Sys.Date()),], select = - Time.1)
      )
    })
    output$historictable <- renderDataTable({
      datatable(
        subset(sensor.data.new, select = - Time.1)
      )
    })
    
    #########  
    # Plots #
    #########  
      ## Font and Titles for Plots  
        plot.font <- list(
                        family = "Arial, sans-serif",
                        size = 18,
                        color = "black"
                      )
      ## Dashboard Plot
        output$today <- renderPlotly({
          plot_ly(sensor.data.new[which(format(sensor.data.new$Date, format = "%y")==Sys.Date()),], x = ~ Time.1, y = ~ Water, name = "% Water Level", type = "scatter", mode = 'lines+markers', marker=list(size=4)) %>%
            add_trace(y = ~Light, name = "% Light", mode = 'lines+markers') %>%
            add_trace(y = ~Leak1, name = "% Leak-1", mode = 'lines+markers') %>%
            add_trace(y = ~Leak2, name = "% Leak-2", mode = 'lines+markers') %>%
            add_trace(y = ~Ambient.Temp, name = "Room Temp", mode = 'lines+markers') %>%
            add_trace(y = ~Tank.Temp, name = "Tank Temp", mode = 'lines+markers') %>%
              layout(
                title = '% Saturation of Water, Light, and Leak Sensors',
                xaxis = list(
                          title = "Date+Time",
                          titlefont = plot.font
                        ),
                yaxis = list(
                          title = "% of Saturation",
                          titlefont = plot.font
                        )
              )
        })
        
      ## Historical Data Plot
        output$historic <- renderPlotly({
          plot_ly(sensor.data.new, x = ~ Time.1, y = ~ Water, name = "% Water Level", type = "scatter", mode = 'lines+markers', marker=list(size=4)) %>%
            add_trace(y = ~Light, name = "% Light", mode = 'lines+markers') %>%
            add_trace(y = ~Leak1, name = "% Leak-1", mode = 'lines+markers') %>%
            add_trace(y = ~Leak2, name = "% Leak-2", mode = 'lines+markers') %>%
            add_trace(y = ~Ambient.Temp, name = "Room Temp", mode = 'lines+markers') %>%
            add_trace(y = ~Tank.Temp, name = "Tank Temp", mode = 'lines+markers') %>%
              layout(
                title = '% Saturation of Water, Light, and Leak Sensors',
                xaxis = list(
                          title = "Date+Time",
                          titlefont = plot.font
                        ),
                yaxis = list(
                          title = "% of Saturation",
                          titlefont = plot.font
                        )
              )
        })
        
    ## Cor plot
        output$corplot <- renderPlot({
            tmp <- subset(sensor.data.new, select = -c(Date, Time, Time.1, Leak1, Leak2))
            M<-cor(tmp, method="spearman", use = "complete.obs")
            cor.mtest <- function(mat, ...) {
                mat <- as.matrix(mat)
                n <- ncol(mat)
                p.mat<- matrix(NA, n, n)
                diag(p.mat) <- 0
                for (i in 1:(n - 1)) {
                    for (j in (i + 1):n) {
                        tmp <- cor.test(mat[, i], mat[, j], ...)
                        p.mat[i, j] <- p.mat[j, i] <- tmp$p.value
                    }
                }
              colnames(p.mat) <- rownames(p.mat) <- colnames(mat)
              p.mat
            }
            # matrix of the p-value of the correlation
            p.mat <- cor.mtest(tmp, method = "spearman", use = "complete.obs")
            corrplot(M, method="circle", type="upper", tl.col = "black", p.mat = p.mat, sig.level = 0.05, 
                     insig = "blank", tl.srt = 45, diag = F, col=brewer.pal(n=8, name="RdBu"), tl.cex=0.9)
        })
  
}
shinyApp(ui, server, options = list(height = 1080))
