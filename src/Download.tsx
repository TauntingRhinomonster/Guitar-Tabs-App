import './Upload.css'
import { useLocation, useNavigate } from 'react-router-dom'
import { PDFDownloadLink, PDFViewer } from '@react-pdf/renderer'
import TabDocument, { type TabData } from './TabDocument'

interface LocationState {

    tabData: TabData

}



export default function DownloadPage() {

    const location = useLocation()
    const navigate = useNavigate()

    const state = location.state as LocationState | null

    const tabData = state?.tabData



    return (

        <div className="upload">

            <nav className="upload-nav">

                <img

                    className="upload-nav__logo"

                    src="/guitar-favicon.png"

                    alt="TabVerter logo"

                />

                <h1 className="upload-nav__title">TabVerter</h1>

            </nav>



            {tabData ? (

                <PDFViewer className="upload-dropzone" width="100%" height="100%">

                    <TabDocument tabData={tabData} />

                </PDFViewer>

            ) : (

                <div className="upload-dropzone">

                    <p className="upload-dropzone__label">

                        No tab data was passed from the previous page.

                    </p>

                </div>

            )}



            {tabData ? (

                <PDFDownloadLink

                    document={<TabDocument tabData={tabData} />}

                    fileName="guitar-tabs.pdf"

                    className="upload-btn"

                >

                    {({ loading }) =>

                        loading ? 'Preparing PDF...' : 'Download Tabs'

                    }

                </PDFDownloadLink>

            ) : (

                <button className="upload-btn" disabled>

                    Download Tabs

                </button>

            )}

            <button className="upload-btn" onClick={() => navigate('/')}>

                Back to Upload

            </button>

        </div>

    )

}


// To view server: 
// $profile
// guitardev