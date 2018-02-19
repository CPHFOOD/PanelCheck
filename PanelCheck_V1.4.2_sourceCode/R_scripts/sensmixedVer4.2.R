
sensmixedVer42=function(frame){

#frame=read.table(name,header=TRUE,sep="\t")

attnames       =  labels(frame)[[2]][-1:-3]                    ; natt  = length(attnames)                                                          # Save the attribute names and number.
ass            =  factor(frame[,1]) ; assnames  = levels(ass)  ; nass  = length(assnames)                                                          # Define as factor, save level names (alphanum.) and #.
prod           =  factor(frame[,2]) ; prodnames = levels(prod) ; nprod = length(prodnames)                                                         #                          -"-
rep            =  factor(frame[,3]) ; repnames  = levels(rep)  ; nrep  = length(repnames)                                                          #                          -"-
nrow           =  dim(frame)[1]                                ; ncol  = dim(frame)[2]                                                             # Number of rows and selected columns in the data frame.
attnames1      =  attnames2 = attnames ; 
if (natt>1) attnames1[seq(2,natt,2)] = '' ; 
attnames2[seq(1,natt,2)] = ''                                           
  # Splitting attnames in two to allow for longer names.

prodFs         =  prodPs = SEs = rep(0,natt)                                                                                                       # Initializing p-value, F-value and SE vectors.
prodco         =  matrix(rep(0,natt*nprod),nrow=natt)                                                                                              # Initialize a natt x nprod matrix for product coefficients. 
const          =  rep(1,nrow)                                                                                                                      # Vector with ones for the design matrix (maybe rubbish!).


aovSS=matrix(rep(0,7*natt),nrow=7)

for (i in 4:ncol){
X=frame[,i]
aovsum =  summary(aov(X ~ ass + prod + rep + ass:prod + ass:rep + prod:rep))
aovSS[,i-3]         =  aovsum[[1]][,2]
}

aovDF=       aovsum[[1]][,1]

Fmatr=matrix(rep(0,9*natt),nrow=9)
Pmatr=matrix(rep(0,9*natt),nrow=9)
LSDmatr=matrix(rep(0,4*natt),nrow=4)

# 2-way analysis:
Fmatr[7,]=(aovSS[2,]/aovDF[2])/(aovSS[4,]/aovDF[4]) 
Fmatr[8,]=(aovSS[1,]/aovDF[1])/(aovSS[4,]/aovDF[4]) 
Fmatr[9,]=(aovSS[4,]/aovDF[4])/((aovSS[3,]+aovSS[5,]+aovSS[6,]+aovSS[7,])/(aovDF[3]+aovDF[5]+aovDF[6]+aovDF[7])) 
Pmatr[7,]=1-pf(Fmatr[7,],aovDF[2],aovDF[4])
Pmatr[8,]=1-pf(Fmatr[8,],aovDF[1],aovDF[4])
Pmatr[9,]=1-pf(Fmatr[9,],aovDF[4],aovDF[3]+aovDF[5]+aovDF[6]+aovDF[7])


# 3-way analysis:

# Fmatr, row 1: 3-way: Ass vs Mixed error (Prod*Ass and Rep*Ass) (*1)
# Fmatr, row 2: 3-way: Prod VS Mixed error (Prod*Ass and Prod*Rep) (*2)
# Fmatr, row 3: 3-way: Rep vs Mixed error (Prod*Rep and Rep*Ass) 
# Fmatr, row 4: 3-way: Prod*Ass vs. Error
# Fmatr, row 5: 3-way: Rep*Ass  vs. Error
# Fmatr, row 6: 3-way: Prod*Rep vs. Error

Fmatr[1,]=(aovSS[1,]/aovDF[1])/(aovSS[4,]/aovDF[4]) 
for (i in 1:natt) if ((aovSS[5,i]/aovDF[5])>(aovSS[7,i]/aovDF[7]))
Fmatr[1,i]=(aovSS[1,i]/aovDF[1])/((aovSS[4,i])/(aovDF[4])+aovSS[5,i]/aovDF[5]-aovSS[7,i]/aovDF[7]) 

Fmatr[2,]=(aovSS[2,]/aovDF[2])/(aovSS[4,]/aovDF[4]) 
for (i in 1:natt) if ((aovSS[6,i]/aovDF[6])>(aovSS[7,i]/aovDF[7]))
Fmatr[2,i]=(aovSS[2,i]/aovDF[2])/((aovSS[4,i])/(aovDF[4])+aovSS[6,i]/aovDF[6]-aovSS[7,i]/aovDF[7]) 

for (i in 1:natt) Fmatr[3,i]=(aovSS[3,i]/aovDF[3])/((aovSS[5,i])/(aovDF[5])+aovSS[6,i]/aovDF[6]-aovSS[7,i]/aovDF[7]) 


Fmatr[4,]=(aovSS[4,]/aovDF[4])/(aovSS[7,]/aovDF[7]) 
Fmatr[5,]=(aovSS[5,]/aovDF[5])/(aovSS[7,]/aovDF[7]) 
Fmatr[6,]=(aovSS[6,]/aovDF[6])/(aovSS[7,]/aovDF[7]) 




Pmatr[4,]=1-pf(Fmatr[4,],aovDF[4],aovDF[7])
Pmatr[5,]=1-pf(Fmatr[5,],aovDF[5],aovDF[7])
Pmatr[6,]=1-pf(Fmatr[6,],aovDF[6],aovDF[7])


DFden1=rep(0,natt)
Pmatr[1,]=1-pf(Fmatr[1,],aovDF[1],aovDF[4])
for (i in 1:natt) if ((aovSS[5,i]/aovDF[5])>(aovSS[7,i]/aovDF[7])){
DFden1[i]=(aovSS[4,i]/aovDF[4]+aovSS[5,i]/aovDF[5]-aovSS[7,i]/aovDF[7])**2/
((((aovSS[4,i])**2)/((aovDF[4])**3)+(aovSS[5,i]**2)/(aovDF[5]**3)+(aovSS[7,i]**2)/(aovDF[7]**3))) 
Pmatr[1,i]=1-pf(Fmatr[1,i],aovDF[1],DFden1[i])
}

DFden2=rep(0,natt)
Pmatr[2,]=1-pf(Fmatr[2,],aovDF[2],aovDF[4])
for (i in 1:natt) if ((aovSS[6,i]/aovDF[6])>(aovSS[7,i]/aovDF[7])){
DFden2[i]=(aovSS[4,i]/aovDF[4]+aovSS[6,i]/aovDF[6]-aovSS[7,i]/aovDF[7])**2/
((((aovSS[4,i])**2)/((aovDF[4])**3)+(aovSS[6,i]**2)/(aovDF[6]**3)+(aovSS[7,i]**2)/(aovDF[7]**3))) 
Pmatr[2,i]=1-pf(Fmatr[2,i],aovDF[2],DFden2[i])
}

DFden3=rep(0,natt)
for (i in 1:natt) {
DFden3[i]=(aovSS[4,i]/aovDF[4]+aovSS[6,i]/aovDF[6]-aovSS[7,i]/aovDF[7])**2/
((((aovSS[4,i])**2)/((aovDF[4])**3)+(aovSS[6,i]**2)/(aovDF[6]**3)+(aovSS[7,i]**2)/(aovDF[7]**3))) 
Pmatr[3,i]=1-pf(Fmatr[3,i],aovDF[3],DFden3[i])
}

Pmatr2=Pmatr
Pmatr2[Pmatr2>0.05]=4
Pmatr2[Pmatr2<0.001]=3
Pmatr2[Pmatr2<0.01]=2
Pmatr2[Pmatr2<0.05]=1
Pmatr2[Pmatr2>3.5]=0


MS=aovSS[4,]/aovDF[4]


LSDmatr[3,]=sqrt(2*MS/(nrep*nass))*qt(0.975,aovDF[4])
LSDmatr[4,]=sqrt(2*MS/(nrep*nass))*qt(1-0.05/(nprod*(nprod-1)),aovDF[4])

LSDmatr[1,]=LSDmatr[3,]
LSDmatr[2,]=LSDmatr[4,]

for (i in 1:natt) if ((aovSS[6,i]/aovDF[6])>(aovSS[7,i]/aovDF[7])){
MS=(aovSS[4,i]/aovDF[4]+aovSS[6,i]/aovDF[6]-aovSS[7,i]/aovDF[7]) 
LSDmatr[1,i]=sqrt(2*MS/(nrep*nass))*qt(0.975,DFden2[i])
LSDmatr[2,i]=sqrt(2*MS/(nrep*nass))*qt(1-0.05/(nprod*(nprod-1)),DFden2[i])
}


list(Fmatr,Pmatr,Pmatr2,LSDmatr)

}

# Fmatr, row 1: 3-way: Ass VS Mixed error (Prod*Ass and Rep*Ass) (*1)
# Fmatr, row 2: 3-way: Prod vs Mixed error (Prod*Ass and Rep*Prod) (*2)
# Fmatr, row 3: 3-way: Rep vs Mixed error (Prod*Rep and Rep*Ass) 
# Fmatr, row 4: 3-way: Prod*Ass vs. Error
# Fmatr, row 5: 3-way: Prod*Rep vs. Error
# Fmatr, row 6: 3-way: Rep*Ass  vs. Error

# Fmatr, row 7: 2-way: Prod vs Prod*Ass
# Fmatr, row 8: 2-way: Ass vs Prod*Ass
# Fmatr, row 9: 2-way: Prod*Ass vs. Error

# (*1) IF the MS(Rep*Ass) is smaller than MS(E) then MS(Prod*Ass) is used.
# (*2) IF the MS(Prod*Rep) is smaller than MS(E) then MS(Prod*Ass) is used.

# Pmatr and Pmatr2 has same structure

# LSDmatr, row 1: 3-way usual LSD
# LSDmatr, row 2: 3-way Bonferroni LSD
# LSDmatr, row 3: 2-way usual LSD
# LSDmatr, row 4: 2-way Bonferroni LSD
 