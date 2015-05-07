import Development.Shake
import Development.Shake.FilePath
import Data.List.Split (splitOn)
import System.FilePath.Glob

dates :: [String]
dates = words "2015-05-05 2015-05-02 2015-04-22 2015-04-20 2015-04-19 2015-04-15 2015-03-19 2015-03-12 2015-02-19 2015-02-17 2015-02-12"

data Date a = Date {year, month, day :: a}

parseDate :: String -> Date String
parseDate s =
    let year:month:day:_ = splitOn "-" s
    in Date year month day

getFiles :: Date String -> IO [FilePath]
getFiles (Date year month day) =
    glob $ concat ["data/by-date/",year,"/",year,"-",month,"/",year,"-",month,"-",day,"/*.timetag"]

main :: IO ()
main = do
    files <- liftIO $ fmap concat $ mapM (getFiles . parseDate) dates
    print files
    shakeArgs shakeOptions $ rules files

rules files = do
    want ["output.pdf"]

    "*.timetag.summary.svg" %> \out -> do
        let timetag = dropExtension $ dropExtension out
        need [timetag]
        need ["scripts/summarize-fcs"]
        cmd "scripts/summarize-fcs" timetag

    "*.pdf" %> \out -> do
        need files
        cmd "svg-nup --no-tidy --nup 1x1 --no-landscape -o" out "--" files
