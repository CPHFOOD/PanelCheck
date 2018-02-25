
sensmixedNoRep11=function(frame){

#frame=read.table(name,header=TRUE,sep="\t")

attnames       =  labels(frame)[[2]][-1:-3]                    ; natt  = length(attnames)                                                          # Save the attribute names and number.
ass            =  factor(frame[,1]) ; assnames  = levels(ass)  ; nass  = length(assnames)                                                          # Define as factor, save level names (alphanum.) and #.
prod           =  factor(frame[,2]) ; prodnames = levels(prod) ; nprod = length(prodnames)                                                         #                          -"-
rep            =  factor(frame[,3]) ; repnames  = levels(rep)  ; nrep  = length(repnames)                                                          #                          -"-
nrow           =  dim(frame)[1]                                ; ncol  = dim(frame)[2]                                                             # Number of rows and selected columns in the data frame.
attnames1      =  attnames2 = attnames ; 
if (natt>1) attnames1[seq(2,natt,2)] = '' ; 
attnames2[seq(1,natt,2)] = ''                                             # Splitting attnames in two to allow for longer names.

prodFs         =  prodPs = SEs = rep(0,natt)                                                                                                       # Initializing p-value, F-value and SE vectors.
prodco         =  matrix(rep(0,natt*nprod),nrow=natt)                                                                                              # Initialize a natt x nprod matrix for product coefficients. 
const          =  rep(1,nrow)                                                                                                                      # Vector with ones for the design matrix (maybe rubbish!).


aovSS=matrix(rep(0,3*natt),nrow=3)

for (i in 4:ncol){
X=frame[,i]
aovsum =  summary(aov(X ~ ass + prod))
aovSS[,i-3]         =  aovsum[[1]][,2]
}

aovDF=       aovsum[[1]][,1]

Fmatr=matrix(rep(0,2*natt),nrow=2)
Pmatr=matrix(rep(0,2*natt),nrow=2)
LSDmatr=matrix(rep(0,2*natt),nrow=2)

Fmatr[1,]=(aovSS[1,]/aovDF[1])/(aovSS[3,]/aovDF[3]) 
Fmatr[2,]=(aovSS[2,]/aovDF[2])/(aovSS[3,]/aovDF[3]) 

Pmatr[1,]=1-pf(Fmatr[1,],aovDF[1],aovDF[3])
Pmatr[2,]=1-pf(Fmatr[2,],aovDF[2],aovDF[3])


Pmatr[Pmatr>0.05]=4
Pmatr[Pmatr<0.001]=3
Pmatr[Pmatr<0.01]=2
Pmatr[Pmatr<0.05]=1
Pmatr[Pmatr>3.5]=0


MS=aovSS[3,]/aovDF[3]

LSDmatr[1,]=sqrt(2*MS/(nrep*nass))*qt(0.975,aovDF[3])
LSDmatr[2,]=sqrt(2*MS/(nrep*nass))*qt(1-0.05/(nprod*(nprod-1)),aovDF[3])

list(Fmatr,Pmatr,LSDmatr)
}

